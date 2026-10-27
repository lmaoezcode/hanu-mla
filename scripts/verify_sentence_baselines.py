"""Independent checks of frozen predictions, metrics and train-only TF-IDF."""

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "experiments" / "sentence-baselines"
LABELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


def csv_rows(filename):
    with (OUT / filename).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    results = json.loads((OUT / "test_results.json").read_text(encoding="utf-8"))
    audit = json.loads((OUT / "data_audit.json").read_text(encoding="utf-8"))
    all_rows = csv_rows("audited_sentences.csv")
    kept = [row for row in all_rows if row["kept"] == "True"]
    train = [row for row in kept if row["split"] == "train"]
    test = [row for row in kept if row["split"] == "test"]
    predictions = csv_rows("test_predictions.csv")
    assert len(all_rows) == 10004 and len(kept) == 10003
    assert len(train) == 7177 and len(test) == len(predictions) == 1460
    assert [row["id"] for row in test] == [row["id"] for row in predictions]
    assert len({row["id"] for row in predictions}) == 1460
    for source in audit["input_manifest"]:
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    checks = {}
    y = np.array([LABELS.index(row["label"]) for row in predictions])
    assert [sum(y == i) for i in range(6)] == [37, 158, 547, 459, 187, 72]
    for name in ["majority", "awl", "tfidf_lr"]:
        p = np.array([LABELS.index(row[f"{name}_prediction"]) for row in predictions])
        matrix = np.zeros((6, 6), dtype=np.int64)
        for true, predicted in zip(y, p):
            matrix[true, predicted] += 1
        score = results["models"][name]
        assert matrix.tolist() == score["confusion_matrix"]
        n = int(matrix.sum())
        diff = np.arange(6)[:, None] - np.arange(6)[None, :]
        observed = float(np.sum(matrix * diff**2))
        expected = float(np.sum(np.outer(matrix.sum(1), matrix.sum(0)) * diff**2) / n)
        qwk = 1 - observed / expected
        mae = float(np.sum(matrix * np.abs(diff)) / n)
        f1 = np.divide(2*np.diag(matrix), matrix.sum(1)+matrix.sum(0), out=np.zeros(6), where=(matrix.sum(1)+matrix.sum(0)) > 0)
        assert abs(qwk - score["qwk"]) < 1e-12
        assert abs(mae - score["mae"]) < 1e-12
        assert abs(float(f1.mean()) - score["macro_f1"]) < 1e-12
        for i in range(6):
            entry = score["per_class"][i]
            assert entry["support"] == int(matrix[i].sum())
            assert entry["predicted_count"] == int(matrix[:, i].sum())
            assert abs(entry["f1"] - f1[i]) < 1e-12
        if name != "majority":
            model_path = "awl_density_tree.joblib" if name == "awl" else "tfidf_lr.joblib"
            model = joblib.load(OUT / model_path)
            x = np.array([[float(row["awl_density"])] for row in test]) if name == "awl" else [row["text"] for row in test]
            assert np.array_equal(model.predict(x), p)
            probs = np.array([[float(row[f"{name}_p_{label}"]) for label in LABELS] for row in predictions])
            assert np.allclose(probs.sum(1), 1)
            assert np.allclose(probs, model.predict_proba(x))
        checks[name] = {"prediction_rows": n, "qwk": qwk, "mae": mae, "macro_f1": float(f1.mean()), "passed": True}
    lr = joblib.load(OUT / "tfidf_lr.joblib")
    vectorizer = lr.named_steps["tfidf"]
    analyzer = vectorizer.build_analyzer()
    counts = Counter(feature for row in train for feature in set(analyzer(row["text"])))
    feature_names = vectorizer.get_feature_names_out()
    expected_idf = np.array([np.log((1+len(train)) / (1+counts[feature])) + 1 for feature in feature_names])
    assert np.allclose(vectorizer.idf_, expected_idf, atol=1e-12, rtol=0)
    assert len(feature_names) == 30000
    checks["train_only_idf"] = {"training_records": len(train), "features_checked": len(feature_names), "passed": True}
    checks["input_sha256"] = {"files_checked": len(audit["input_manifest"]), "passed": True}
    report = {"checks": checks, "all_passed": True,
              "scope": "Independent arithmetic from saved predictions, source hashes, saved-model predictions/probabilities and IDF reconstructed solely from train. No model reselection or refitting."}
    (OUT / "verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
