"""Controlled source check and reproducible case selection on train and dev only.

Test rows are dropped immediately after loading. The frozen models are not changed.
Pre-run assumption: balancing source weights improves QWK and MAE on dev SCoRE and
may reduce them on dev Wiki-Auto.
"""

import csv
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import cohen_kappa_score, f1_score, mean_absolute_error
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output" / "experiments" / "sentence-baselines"
OUT = ROOT / "output" / "experiments" / "dev-checks"
LABELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
SEED = 20261004
SOURCES = ["SCoRE", "Wiki-Auto"]


def load_rows():
    with (BASE / "audited_sentences.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row["kept"] == "True" and row["split"] in {"train", "dev"}]
    for row in rows:
        for key in ["target", "annotator_1", "annotator_2", "word_count", "awl_count"]:
            row[key] = int(row[key])
        row["awl_density"] = float(row["awl_density"])
    return [row for row in rows if row["split"] == "train"], [row for row in rows if row["split"] == "dev"]


def score(y, prediction):
    labels = list(range(6))
    return {"n": len(y), "qwk": float(cohen_kappa_score(y, prediction, labels=labels, weights="quadratic")),
            "mae": float(mean_absolute_error(y, prediction)),
            "macro_f1": float(f1_score(y, prediction, labels=labels, average="macro", zero_division=0))}


def scores_by_source(dev, y, prediction):
    result = {"Tat ca": score(y, prediction)}
    for source in SOURCES:
        mask = np.array([row["corpus_source"] == source for row in dev])
        result[source] = score(y[mask], prediction[mask])
    return result


def controlled_check(train, dev):
    # Same features, C, class weights and seed as the frozen model. Only the source weight changes.
    y_train = np.array([row["target"] for row in train])
    y_dev = np.array([row["target"] for row in dev])
    x_train = [row["text"] for row in train]
    x_dev = [row["text"] for row in dev]
    sources = np.array([row["corpus_source"] for row in train])
    class_counts = np.bincount(y_train, minlength=6)
    class_weight = len(train) / (6 * class_counts)
    source_weight = {source: len(train) / (2 * int((sources == source).sum())) for source in SOURCES}

    def fit(sample_weight):
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=1.0, max_features=30000,
                                     sublinear_tf=True, lowercase=True)
        classifier = LogisticRegression(C=10.0, solver="lbfgs", penalty="l2", max_iter=2000, random_state=SEED)
        classifier.fit(vectorizer.fit_transform(x_train), y_train, sample_weight=sample_weight)
        return Pipeline([("tfidf", vectorizer), ("lr", classifier)])

    balanced_only = class_weight[y_train]
    with_source = balanced_only * np.array([source_weight[source] for source in sources])
    frozen = joblib.load(BASE / "tfidf_lr.joblib")
    refit = fit(balanced_only)
    changed = fit(with_source)
    assert np.array_equal(refit.predict(x_dev), frozen.predict(x_dev)), "Refit must reproduce the frozen model on dev"
    result = {
        "question": "Does the source imbalance between train and dev weaken LR on SCoRE sentences?",
        "pre_run_assumption": "Balancing source weights improves QWK and MAE on dev SCoRE and may reduce them on dev Wiki-Auto.",
        "change": "One factor: sample_weight also balances total SCoRE and Wiki-Auto weight in train.",
        "fixed": {"C": 10.0, "min_df": 1, "ngram_range": [1, 2], "max_features": 30000, "seed": SEED},
        "source_weight": source_weight,
        "train_counts": {source: int((sources == source).sum()) for source in SOURCES},
        "test_used": False,
        "frozen_model_replaced": False,
        "frozen_lr": scores_by_source(dev, y_dev, frozen.predict(x_dev)),
        "source_balanced_lr": scores_by_source(dev, y_dev, changed.predict(x_dev)),
    }
    (OUT / "controlled_source_check.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    with (OUT / "controlled_source_check.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["model", "scope", "n", "qwk", "mae", "macro_f1"])
        writer.writeheader()
        for model in ["frozen_lr", "source_balanced_lr"]:
            for scope, values in result[model].items():
                writer.writerow({"model": model, "scope": scope, **values})
    return result


def sample_by_label(rows, per_label, rng):
    # Rule: random with a fixed seed, at most per_label rows for each true label, sorted by ID first.
    chosen = []
    for target in range(6):
        group = sorted((row for row in rows if row["target"] == target), key=lambda row: row["id"])
        if group:
            indices = rng.choice(len(group), size=min(per_label, len(group)), replace=False)
            chosen.extend(group[int(i)] for i in sorted(indices))
    return chosen


def top_features(model, text, target_class):
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["lr"]
    names = vectorizer.get_feature_names_out()
    vector = vectorizer.transform([text])
    rows = [(names[i], float(vector[0, i] * classifier.coef_[target_class, i])) for i in vector.nonzero()[1]]
    rows.sort(key=lambda row: -row[1])
    return "; ".join(f"{name} {value:+.2f}" for name, value in rows[:4])


def select_cases(dev):
    lr = joblib.load(BASE / "tfidf_lr.joblib")
    tree = joblib.load(BASE / "awl_density_tree.joblib")
    lr_prediction = lr.predict([row["text"] for row in dev])
    probabilities = lr.predict_proba([row["text"] for row in dev])
    tree_prediction = tree.predict(np.array([[row["awl_density"]] for row in dev]))
    for row, lr_p, tree_p, probs in zip(dev, lr_prediction, tree_prediction, probabilities):
        row["lr"], row["tree"], row["lr_probability"] = int(lr_p), int(tree_p), float(probs[int(lr_p)])
    pools = {
        "Ko_loi_LR_lech_2_bac": [row for row in dev if abs(row["lr"] - row["target"]) >= 2],
        "Ka_bat_dong_nhan": [row for row in dev if row["annotator_1"] != row["annotator_2"]],
        "Ka_cay_AWL_sai": [row for row in dev if abs(row["tree"] - row["target"]) >= 2],
    }
    plan = {"Ko_loi_LR_lech_2_bac": 2, "Ka_bat_dong_nhan": 1, "Ka_cay_AWL_sai": 1}
    rng = np.random.default_rng(SEED)
    cases = []
    for group, rows in pools.items():
        for row in sample_by_label(rows, plan[group], rng):
            cases.append({
                "group": group, "id": row["id"], "text": row["text"], "source": row["corpus_source"],
                "annotator_1": LABELS[row["annotator_1"]], "annotator_2": LABELS[row["annotator_2"]],
                "target": LABELS[row["target"]], "lr_prediction": LABELS[row["lr"]],
                "lr_probability": round(row["lr_probability"], 3), "tree_prediction": LABELS[row["tree"]],
                "word_count": row["word_count"], "awl_count": row["awl_count"],
                "awl_density": round(row["awl_density"], 4),
                "top_features_for_lr_prediction": top_features(lr, row["text"], row["lr"]),
            })
    with (OUT / "selected_cases.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(cases[0]))
        writer.writeheader()
        writer.writerows(cases)
    return {group: len(rows) for group, rows in pools.items()}, len(cases)


def group_summary(rows, prediction_key):
    errors = [row[prediction_key] - row["target"] for row in rows]
    return {"n": len(rows),
            "correct": sum(error == 0 for error in errors),
            "predicted_too_high": sum(error > 0 for error in errors),
            "predicted_too_low": sum(error < 0 for error in errors),
            "mean_signed_error": float(np.mean(errors)) if errors else None}


def hypothesis_checks(dev):
    # Run after select_cases, which adds the saved models' dev predictions to each row.
    lr = joblib.load(BASE / "tfidf_lr.joblib")
    analyzer = lr.named_steps["tfidf"].build_analyzer()
    vocabulary = lr.named_steps["tfidf"].vocabulary_
    for row in dev:
        words = [token for token in analyzer(row["text"]) if " " not in token]
        row["unseen_share"] = sum(token not in vocabulary for token in words) / max(len(words), 1)
    high = [row for row in dev if row["target"] >= 4]
    disagreement = [row for row in dev if row["annotator_1"] != row["annotator_2"]]
    agreement = [row for row in dev if row["annotator_1"] == row["annotator_2"]]
    zero_awl = [row for row in dev if row["awl_count"] == 0]
    result = {
        "short_sentences_up_to_7_words_lr": group_summary([row for row in dev if row["word_count"] <= 7], "lr"),
        "long_sentences_over_15_words_lr": group_summary([row for row in dev if row["word_count"] > 15], "lr"),
        "short_a1_a2_lr": group_summary([row for row in dev if row["word_count"] <= 7 and row["target"] <= 1], "lr"),
        "short_b2_c1_c2_lr": group_summary([row for row in dev if row["word_count"] <= 7 and row["target"] >= 3], "lr"),
        "c1_c2_unseen_word_share": {
            "correct_mean": float(np.mean([row["unseen_share"] for row in high if row["lr"] == row["target"]])),
            "too_low_mean": float(np.mean([row["unseen_share"] for row in high if row["lr"] < row["target"]])),
            "correct_n": sum(row["lr"] == row["target"] for row in high),
            "too_low_n": sum(row["lr"] < row["target"] for row in high),
        },
        "label_disagreement": {
            "disagree_n": len(disagreement), "agree_n": len(agreement),
            "lr_accuracy_when_disagree": float(np.mean([row["lr"] == row["target"] for row in disagreement])),
            "lr_accuracy_when_agree": float(np.mean([row["lr"] == row["target"] for row in agreement])),
            "lr_matches_either_label_when_disagree": float(np.mean(
                [row["lr"] in (row["annotator_1"], row["annotator_2"]) for row in disagreement])),
        },
        "tree_zero_awl": {
            "zero_awl_n": len(zero_awl),
            "predicted_a1": sum(row["tree"] == 0 for row in zero_awl),
            "true_a1": sum(row["target"] == 0 for row in zero_awl),
            "true_b2_or_higher": sum(row["target"] >= 3 for row in zero_awl),
        },
        "dev_counts": {"predicted_a1_by_tree": sum(row["tree"] == 0 for row in dev), "true_a1": sum(row["target"] == 0 for row in dev)},
    }
    (OUT / "hypothesis_checks.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    train, dev = load_rows()
    assert len(train) == 7177 and len(dev) == 1366
    result = controlled_check(train, dev)
    print(json.dumps({key: result[key] for key in ["frozen_lr", "source_balanced_lr"]}, indent=1))
    print(select_cases(dev))
    print(json.dumps(hypothesis_checks(dev), indent=1))


if __name__ == "__main__":
    main()
