"""Reproducible CEFR-SP sentence baselines with a separate test phase.

Run with the project environment, not the document-rendering interpreter.
Selection does not compute test scores. Test evaluation loads frozen models.
"""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, export_text

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "experiments" / "sentence-baselines"
LABELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
SEED = 20261004
WORD_PATTERN = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*")
FORM_PATTERN = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*")
AWL_GRID = [
    {"max_leaf_nodes": leaves, "min_samples_leaf": minimum, "class_weight": weight}
    for leaves in [2, 3, 6]
    for minimum in [50, 100, 200]
    for weight in [None, "balanced"]
]
LR_GRID = [
    {"C": c, "min_df": minimum}
    for c in [0.1, 1.0, 10.0]
    for minimum in [1, 2]
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_text(text):
    return " ".join(text.split())


def word_tokens(text):
    # Hyphenated words and attached contractions each count as one token.
    # Numeric strings and punctuation are excluded; no stemming is used.
    return WORD_PATTERN.findall(text.replace("\u2019", "'").replace("\u2018", "'").lower())


def parse_awl():
    source = ROOT / "data" / "awl" / "awl-families.pdf"
    head_source = ROOT / "data" / "awl" / "awl-headwords.pdf"
    head_text = "\n".join(page.extract_text() for page in PdfReader(head_source).pages)
    heads = dict(re.findall(r"^\s*([A-Za-z]+(?:-[A-Za-z]+)*)\s+(10|[1-9])\s*$", head_text, re.M))
    assert len(heads) == 570, f"Expected 570 AWL families, got {len(heads)}"
    rows = []
    current_sublist = None
    seen_sublists = set()
    for page_number, page in enumerate(PdfReader(source).pages, 1):
        for line in page.extract_text().splitlines():
            heading = re.search(r"Sublist\s+(10|[1-9])\b", line)
            if heading:
                current_sublist = int(heading.group(1))
                seen_sublists.add(current_sublist)
            form = line.strip().lower()
            if not FORM_PATTERN.fullmatch(form):
                continue
            assert current_sublist is not None, (page_number, line)
            # Do not infer family boundaries from PDF indentation: the headword
            # and sublist PDFs sometimes use different representative members.
            rows.append({"form": form, "sublist": current_sublist, "pdf_page": page_number})
    forms = {row["form"] for row in rows}
    assert set(heads) <= forms, f"Missing headwords: {set(heads) - forms}"
    assert seen_sublists == set(range(1, 11))
    assert {"analyse", "analysis", "analyze", "contextualise", "contextualize", "so-called"} <= forms
    assert "the" not in forms
    assert len(forms) == 3111, f"Unexpected extraction count: {len(forms)}"
    write_csv(OUT / "awl_forms.csv", rows)
    write_json(OUT / "awl_manifest.json", {
        "family_count": len(heads), "distinct_forms": len(forms), "extracted_rows": len(rows),
        "family_pdf_sha256": sha256(source), "headword_pdf_sha256": sha256(head_source),
        "family_url": "https://www.wgtn.ac.nz/lals/resources/academicwordlist/publications/awlsublists1.pdf",
        "headword_url": "https://www.wgtn.ac.nz/lals/resources/academicwordlist/awl-headwords/Headwords-of-the-Academic-Word-List.pdf",
        "definition": "AWL occurrences / alphabetic word-token count; case-insensitive exact matching against all listed forms, repeated occurrences included; no stemming; hyphenated words count once.",
        "license_note": "No open license is asserted for the AWL PDFs. Sources are retained for this educational project; check permissions before redistribution.",
    })
    return forms


def audit_data(forms):
    hf_path = ROOT / "data" / "cefr-sp" / "cefr-sp.json"
    hf = json.loads(hf_path.read_text(encoding="utf-8"))
    hf_counter = Counter((normalized_text(row["text"]), LABELS.index(row["cefr_level"])) for row in hf)
    hf_lookup = defaultdict(list)
    for row in hf:
        hf_lookup[(normalized_text(row["text"]), LABELS.index(row["cefr_level"]))].append(row)
    rows = []
    inputs = [{"path": str(hf_path.relative_to(ROOT)), "sha256": sha256(hf_path), "bytes": hf_path.stat().st_size,
               "url": "https://huggingface.co/datasets/UniversalCEFR/cefr_sp_en/resolve/main/cefr-sp.json"}]
    for split in ["train", "dev", "test"]:
        for source in ["score", "wiki"]:
            path = ROOT / "data" / "cefr-sp" / "official" / f"{source}_{split}.txt"
            source_folder = "SCoRE" if source == "score" else "Wiki-Auto"
            source_name = "SCoRE" if source == "score" else "Wikiauto"
            inputs.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "bytes": path.stat().st_size,
                           "url": f"https://raw.githubusercontent.com/yukiar/CEFR-SP/main/CEFR-SP/{source_folder}/CEFR-SP_{source_name}_{split}.txt"})
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                text, label1, label2 = line.split("\t")
                a, b = int(label1) - 1, int(label2) - 1
                target = max(a, b)
                key = normalized_text(text), target
                assert key in hf_lookup, (path, line_number)
                metadata = hf_lookup[key][0]
                tokens = word_tokens(text)
                awl_count = sum(token in forms for token in tokens)
                rows.append({
                    "id": f"{source}_{split}_{line_number:04d}", "text": text, "split": split,
                    "corpus_source": "SCoRE" if source == "score" else "Wiki-Auto",
                    "annotator_1": a, "annotator_2": b, "target": target,
                    "cefr_level": LABELS[target], "word_count": len(tokens), "space_token_count": len(text.split()), "awl_count": awl_count,
                    "awl_density": awl_count / len(tokens),
                    "hf_license": metadata["license"],
                    "source_license": "CC BY-NC-SA 4.0" if source == "score" else "CC BY-SA 3.0",
                    "kept": True,
                })
    official_counter = Counter((normalized_text(row["text"]), row["target"]) for row in rows)
    assert hf_counter == official_counter, "HF rows do not match the official files"
    assert len(rows) == len(hf) == 10004
    raw_counts = Counter(row["split"] for row in rows)
    assert raw_counts == {"train": 7178, "dev": 1366, "test": 1460}
    overlaps = {}
    for a, b in [("train", "dev"), ("train", "test"), ("dev", "test")]:
        texts_a = {normalized_text(row["text"]) for row in rows if row["split"] == a}
        texts_b = {normalized_text(row["text"]) for row in rows if row["split"] == b}
        intersection = texts_a & texts_b
        overlaps[f"{a}_{b}"] = len(intersection)
        assert not intersection, f"Unexpected exact cross-split overlap: {a}, {b}"
    seen = {}
    duplicates = []
    for row in rows:
        if row["split"] != "train":
            continue
        key = normalized_text(row["text"])
        if key in seen:
            prior = seen[key]
            assert prior["target"] == row["target"], "Duplicate sentence has conflicting targets"
            row["kept"] = False
            duplicates.append({"removed_id": row["id"], "retained_id": prior["id"],
                               "text": row["text"], "cefr_level": row["cefr_level"],
                               "retained_annotators": [prior["annotator_1"], prior["annotator_2"]],
                               "removed_annotators": [row["annotator_1"], row["annotator_2"]]})
        else:
            seen[key] = row
    assert len(duplicates) == 1
    kept = [row for row in rows if row["kept"]]
    assert Counter(row["split"] for row in kept) == {"train": 7177, "dev": 1366, "test": 1460}
    test_support = Counter(row["target"] for row in kept if row["split"] == "test")
    assert [test_support[i] for i in range(6)] == [37, 158, 547, 459, 187, 72]
    differences = Counter(abs(row["annotator_1"] - row["annotator_2"]) for row in rows)
    assert set(differences) <= {0, 1}
    train = [row for row in kept if row["split"] == "train"]
    df = Counter(token for row in train for token in set(word_tokens(row["text"])))
    # An internal rarity diagnostic, not a general English frequency lexicon.
    for row in rows:
        tokens = word_tokens(row["text"])
        row["train_rare_word_ratio"] = sum(df[token] <= 5 for token in tokens) / len(tokens)
    write_csv(OUT / "audited_sentences.csv", rows)
    summary = {
        "input_manifest": inputs, "target_definition": "Higher of the two expert labels, matching every HF record",
        "hf_official_multiset_match": True, "raw_split_counts": dict(raw_counts),
        "used_split_counts": dict(Counter(row["split"] for row in kept)), "removed_duplicates": duplicates,
        "exact_cross_split_overlaps": overlaps,
        "public_label_distribution": {label: sum(row["target"] == i for row in rows) for i, label in enumerate(LABELS)},
        "annotator_exact_agreement": differences[0] / len(rows), "annotator_distance_counts": dict(differences),
        "tokenizer": WORD_PATTERN.pattern,
        "word_length": {"min": min(row["word_count"] for row in rows), "max": max(row["word_count"] for row in rows),
                        "mean": float(np.mean([row["word_count"] for row in rows])),
                        "median": float(np.median([row["word_count"] for row in rows]))},
        "space_token_length": {"min": min(row["space_token_count"] for row in rows), "max": max(row["space_token_count"] for row in rows),
                               "mean": float(np.mean([row["space_token_count"] for row in rows])),
                               "median": float(np.median([row["space_token_count"] for row in rows]))},
        "length_unit_note": "The earlier 5-34 range and 14.8 mean count whitespace tokens, including punctuation and numerals. Alphabetic word tokens under this experiment's explicit regex have range 2-31 and mean 13.0; the figures are not interchangeable.",
        "rare_word_definition": "Fraction of word tokens with document frequency <= 5 in deduplicated train, including unseen tokens; this is corpus-relative rarity, not learner familiarity.",
        "annotation_caution": "41.4% agreement pertains to the filtered public subset. The original study excluded larger disagreements; it is not the raw annotation agreement.",
        "leakage_caution": "Exact overlaps were checked here. Near-similarity separation relies on the authors' split design; absent document IDs, this is not a claim of complete document-level leakage prevention.",
    }
    write_json(OUT / "data_audit.json", summary)
    eda = []
    for split in ["train", "dev", "test"]:
        for i, label in enumerate(LABELS):
            group = [row for row in kept if row["split"] == split and row["target"] == i]
            eda.append({
                "split": split, "cefr_level": label, "support": len(group),
                "word_count_mean": float(np.mean([row["word_count"] for row in group])),
                "word_count_median": float(np.median([row["word_count"] for row in group])),
                "awl_density_mean": float(np.mean([row["awl_density"] for row in group])),
                "zero_awl_fraction": float(np.mean([row["awl_count"] == 0 for row in group])),
                "train_rare_word_ratio_mean": float(np.mean([row["train_rare_word_ratio"] for row in group])),
                "score_count": sum(row["corpus_source"] == "SCoRE" for row in group),
                "wiki_count": sum(row["corpus_source"] == "Wiki-Auto" for row in group),
            })
    write_csv(OUT / "eda_by_level.csv", eda)
    return kept, summary


def metrics(y, prediction):
    return {
        "qwk": float(cohen_kappa_score(y, prediction, labels=list(range(6)), weights="quadratic")),
        "mae": float(mean_absolute_error(y, prediction)),
        "macro_f1": float(f1_score(y, prediction, labels=list(range(6)), average="macro", zero_division=0)),
        "accuracy": float(accuracy_score(y, prediction)),
    }


def selection_key(candidate):
    score = candidate["validation"]
    # Grid order is the final deterministic tie-break; simpler trees come first.
    return score["qwk"], -score["mae"], score["macro_f1"]


def load_records():
    with (OUT / "audited_sentences.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows = [row for row in rows if row["kept"] == "True"]
    for row in rows:
        for key in ["target", "annotator_1", "annotator_2", "word_count", "awl_count"]:
            row[key] = int(row[key])
        row["awl_density"] = float(row["awl_density"])
    return rows


def select_models(rows, audit):
    train = [row for row in rows if row["split"] == "train"]
    dev = [row for row in rows if row["split"] == "dev"]
    y_train = np.array([row["target"] for row in train])
    y_dev = np.array([row["target"] for row in dev])
    x_awl_train = np.array([[row["awl_density"]] for row in train])
    x_awl_dev = np.array([[row["awl_density"]] for row in dev])
    x_text_train = [row["text"] for row in train]
    x_text_dev = [row["text"] for row in dev]
    plan = {"created_utc": utc_now(), "seed": SEED, "label_order": LABELS,
            "selection_rule": "Maximum validation QWK, then lower validation MAE, then higher macro-F1, then first grid entry",
            "awl_grid": AWL_GRID, "lr_grid": LR_GRID,
            "fixed_lr": {"ngram_range": [1, 2], "max_features": 30000, "max_df": 1.0, "sublinear_tf": True,
                         "class_weight": "balanced", "solver": "lbfgs", "penalty": "l2", "max_iter": 2000},
            "test_not_used_for_selection": True, "input_manifest": audit["input_manifest"]}
    write_json(OUT / "selection_plan.json", plan)
    majority = int(np.argmax(np.bincount(y_train, minlength=6)))
    candidates = []
    best_awl = None
    best_awl_entry = None
    for config in AWL_GRID:
        model = DecisionTreeClassifier(**config, random_state=SEED)
        model.fit(x_awl_train, y_train)
        entry = {"family": "awl", "config": config, "validation": metrics(y_dev, model.predict(x_awl_dev))}
        candidates.append(entry)
        if best_awl_entry is None or selection_key(entry) > selection_key(best_awl_entry):
            best_awl, best_awl_entry = model, entry
    print("Selected AWL", json.dumps(best_awl_entry), flush=True)
    best_lr = None
    best_lr_entry = None
    for config in LR_GRID:
        model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=config["min_df"], max_df=1.0,
                                      max_features=30000, sublinear_tf=True, lowercase=True)),
            ("lr", LogisticRegression(C=config["C"], solver="lbfgs", penalty="l2", class_weight="balanced",
                                      max_iter=2000, random_state=SEED)),
        ])
        started = time.monotonic()
        model.fit(x_text_train, y_train)
        entry = {"family": "tfidf_lr", "config": config, "validation": metrics(y_dev, model.predict(x_text_dev)),
                 "fit_seconds": time.monotonic() - started,
                 "feature_count": len(model.named_steps["tfidf"].vocabulary_),
                 "iterations": int(model.named_steps["lr"].n_iter_.max())}
        assert entry["iterations"] < 2000, "LR did not converge"
        candidates.append(entry)
        print("LR candidate", json.dumps(entry), flush=True)
        if best_lr_entry is None or selection_key(entry) > selection_key(best_lr_entry):
            best_lr, best_lr_entry = model, entry
    selected = {
        "selected_utc": utc_now(), "majority_label": LABELS[majority], "majority_target": majority,
        "majority_validation": metrics(y_dev, np.full(len(dev), majority)),
        "awl": best_awl_entry, "tfidf_lr": best_lr_entry,
        "test_evaluated": False,
        "train_class_counts": {LABELS[i]: int(sum(y_train == i)) for i in range(6)},
        "train_class_weights": {LABELS[i]: len(train) / (6 * int(sum(y_train == i))) for i in range(6)},
    }
    write_json(OUT / "validation_candidates.json", candidates)
    write_json(OUT / "frozen_selection.json", selected)
    joblib.dump(best_awl, OUT / "awl_density_tree.joblib")
    joblib.dump(best_lr, OUT / "tfidf_lr.joblib")
    (OUT / "awl_tree_rules.txt").write_text(export_text(best_awl, feature_names=["AWL density"], decimals=6), encoding="utf-8")
    features = best_lr.named_steps["tfidf"].get_feature_names_out()
    coefficients = best_lr.named_steps["lr"].coef_
    top_rows = []
    for i, label in enumerate(LABELS):
        for rank, index in enumerate(np.argsort(coefficients[i])[::-1][:20], 1):
            top_rows.append({"cefr_level": label, "rank": rank, "feature": str(features[index]), "coefficient": float(coefficients[i, index])})
    write_csv(OUT / "lr_top_coefficients.csv", top_rows)
    write_json(OUT / "environment.json", {
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: importlib.metadata.version(name) for name in ["scikit-learn", "numpy", "scipy", "joblib", "pypdf"]},
    })
    print("Models and selection frozen; no test scores computed.", flush=True)


def fast_bootstrap_metrics(y, prediction):
    matrix = np.bincount(y * 6 + prediction, minlength=36).reshape(6, 6)
    n = int(matrix.sum())
    distance = np.subtract.outer(np.arange(6), np.arange(6))
    squared = distance ** 2
    observed = float((matrix * squared).sum())
    expected = float((np.outer(matrix.sum(axis=1), matrix.sum(axis=0)) * squared).sum() / n)
    qwk = 1 - observed / expected if expected > 0 else 0.0
    mae = float((matrix * abs(distance)).sum() / n)
    denom = matrix.sum(axis=1) + matrix.sum(axis=0)
    f1 = np.divide(2 * np.diag(matrix), denom, out=np.zeros(6, dtype=float), where=denom > 0)
    return {"qwk": qwk, "mae": mae, "macro_f1": float(f1.mean())}


def test_models(rows):
    selected = json.loads((OUT / "frozen_selection.json").read_text(encoding="utf-8"))
    if (OUT / "test_results.json").exists():
        raise RuntimeError("Test results already exist. Do not tune models against them or silently overwrite the test run.")
    test = [row for row in rows if row["split"] == "test"]
    y = np.array([row["target"] for row in test])
    awl = joblib.load(OUT / "awl_density_tree.joblib")
    lr = joblib.load(OUT / "tfidf_lr.joblib")
    x_awl = np.array([[row["awl_density"]] for row in test])
    x_text = [row["text"] for row in test]
    predictions = {
        "majority": np.full(len(test), selected["majority_target"]),
        "awl": awl.predict(x_awl),
        "tfidf_lr": lr.predict(x_text),
    }
    probabilities = {"awl": awl.predict_proba(x_awl), "tfidf_lr": lr.predict_proba(x_text)}
    result = {"evaluated_utc": utc_now(), "test_support": {LABELS[i]: int(sum(y == i)) for i in range(6)},
              "target": "max(annotator_1, annotator_2); HF convention",
              "bootstrap": {"replicates": 1000, "seed": SEED,
                            "method": "Stratified by true CEFR label, paired test-row indices across models; percentile 95% intervals",
                            "limitation": "Fixed fitted models and fixed test class proportions; does not cover training variability or domain shift."},
              "models": {}}
    per_class_rows = []
    source_rows = []
    for name, pred in predictions.items():
        score = metrics(y, pred)
        matrix = confusion_matrix(y, pred, labels=list(range(6)))
        p, r, f, support = precision_recall_fscore_support(y, pred, labels=list(range(6)), zero_division=0)
        score["confusion_matrix"] = matrix.tolist()
        score["per_class"] = [{"label": label, "precision": float(p[i]), "recall": float(r[i]),
                               "f1": float(f[i]), "support": int(support[i]), "predicted_count": int(sum(pred == i))}
                              for i, label in enumerate(LABELS)]
        score["per_source"] = {}
        for source in ["SCoRE", "Wiki-Auto"]:
            mask = np.array([row["corpus_source"] == source for row in test])
            source_score = {**metrics(y[mask], pred[mask]), "n": int(mask.sum()),
                            "support": {LABELS[i]: int(sum(y[mask] == i)) for i in range(6)}}
            score["per_source"][source] = source_score
            source_rows.append({"model": name, "source": source, **{key: source_score[key] for key in ["n", "qwk", "mae", "macro_f1", "accuracy"]}})
        result["models"][name] = score
        per_class_rows.extend({"model": name, **entry} for entry in score["per_class"])
        # Check independent formulas used for fast bootstrap against sklearn.
        fast = fast_bootstrap_metrics(y, pred)
        assert all(abs(fast[key] - score[key]) < 1e-12 for key in fast)
    indices_by_class = [np.flatnonzero(y == i) for i in range(6)]
    rng = np.random.default_rng(SEED)
    bootstrap_values = {name: {key: [] for key in ["qwk", "mae", "macro_f1"]} for name in predictions}
    for _ in range(1000):
        index = np.concatenate([rng.choice(group, size=len(group), replace=True) for group in indices_by_class])
        for name, pred in predictions.items():
            score = fast_bootstrap_metrics(y[index], pred[index])
            for key, value in score.items():
                bootstrap_values[name][key].append(value)
    for name in predictions:
        result["models"][name]["ci95"] = {key: [float(x) for x in np.percentile(values, [2.5, 97.5])]
                                                 for key, values in bootstrap_values[name].items()}
    prediction_rows = []
    for index, row in enumerate(test):
        entry = {"id": row["id"], "text": row["text"], "source": row["corpus_source"],
                 "label": row["cefr_level"], "annotator_1": LABELS[row["annotator_1"]],
                 "annotator_2": LABELS[row["annotator_2"]], "word_count": row["word_count"],
                 "awl_density": row["awl_density"],
                 **{f"{name}_prediction": LABELS[int(pred[index])] for name, pred in predictions.items()}}
        for name, probs in probabilities.items():
            for column, label in enumerate(LABELS):
                entry[f"{name}_p_{label}"] = float(probs[index, column])
        prediction_rows.append(entry)
    write_csv(OUT / "test_predictions.csv", prediction_rows)
    write_csv(OUT / "per_class_test.csv", per_class_rows)
    write_csv(OUT / "per_source_test.csv", source_rows)
    write_csv(OUT / "test_metrics.csv", [
        {"model": name, **{key: score[key] for key in ["qwk", "mae", "macro_f1", "accuracy"]},
         **{f"{key}_ci_{bound}": score["ci95"][key][j] for key in ["qwk", "mae", "macro_f1"]
            for j, bound in enumerate(["low", "high"])}}
        for name, score in result["models"].items()
    ])
    write_json(OUT / "test_results.json", result)
    selected["test_evaluated"] = True
    selected["test_evaluated_utc"] = result["evaluated_utc"]
    write_json(OUT / "frozen_selection.json", selected)
    for name, score in result["models"].items():
        print(name, {key: score[key] for key in ["qwk", "mae", "macro_f1", "accuracy"]}, flush=True)


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["audit", "select", "test"], required=True)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    OUT = args.output_dir.resolve()
    if not OUT.is_relative_to(ROOT):
        raise ValueError("Experiment outputs must stay inside the project directory")
    OUT.mkdir(parents=True, exist_ok=True)
    if args.phase == "audit":
        forms = parse_awl()
        _, audit = audit_data(forms)
        # Correct provenance/length-unit metadata without refitting frozen models.
        plan_path = OUT / "selection_plan.json"
        if plan_path.exists():
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["input_manifest"] = audit["input_manifest"]
            plan["metadata_verified_utc"] = utc_now()
            write_json(plan_path, plan)
        print(json.dumps(audit["space_token_length"]), flush=True)
    elif args.phase == "select":
        if (OUT / "frozen_selection.json").exists():
            raise RuntimeError("A frozen selection already exists. Preserve the original experiment before running a new study.")
        forms = parse_awl()
        rows, audit = audit_data(forms)
        print("Data audit", json.dumps({key: audit[key] for key in ["used_split_counts", "public_label_distribution", "word_length", "annotator_exact_agreement"]}), flush=True)
        select_models(rows, audit)
    else:
        test_models(load_records())


if __name__ == "__main__":
    main()
