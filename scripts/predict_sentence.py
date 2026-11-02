"""Explain the saved models' predictions for one sentence. Reads saved files only."""

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_sentence_baselines import LABELS, word_tokens  # noqa: E402

DEFAULT_DIR = ROOT / "output" / "experiments" / "sentence-baselines"


def explain(sentence, out):
    selected = json.loads((out / "frozen_selection.json").read_text(encoding="utf-8"))
    forms = {line.split(",")[0] for line in (out / "awl_forms.csv").read_text(encoding="utf-8-sig").splitlines()[1:]}
    tree = joblib.load(out / "awl_density_tree.joblib")
    model = joblib.load(out / "tfidf_lr.joblib")

    print(f"\nCau: {sentence}")
    print(f"\n[1] Majority: luon doan {selected['majority_label']}")

    tokens = word_tokens(sentence)
    matches = [token for token in tokens if token in forms]
    density = len(matches) / len(tokens) if tokens else 0.0
    print(f"\n[2] Cay AWL: {len(matches)} tu AWL {matches} / {len(tokens)} tu = mat do {density:.4f}")
    print(f"    Du doan: {LABELS[int(tree.predict([[density]])[0])]}")

    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["lr"]
    names = vectorizer.get_feature_names_out()
    vector = vectorizer.transform([sentence])
    probabilities = model.predict_proba([sentence])[0]
    best = int(np.argmax(probabilities))
    print(f"\n[3] TF-IDF + LR: du doan {LABELS[best]}")
    print("    Xac suat: " + "  ".join(f"{label} {p:.3f}" for label, p in zip(LABELS, probabilities)))
    indices = vector.nonzero()[1]
    print(f"    So dac trung tim thay: {len(indices)}")
    print(f"    Diem cua {LABELS[best]} = he so chan {classifier.intercept_[best]:+.3f} + tong cac dong gop:")
    rows = sorted(((names[i], vector[0, i], classifier.coef_[best, i]) for i in indices),
                  key=lambda row: -abs(row[1] * row[2]))
    for name, value, coefficient in rows[:8]:
        print(f"      {name:<24} tfidf {value:.3f} x he so {coefficient:+.2f} = {value * coefficient:+.3f}")
    if not rows:
        print("      (khong co tu nao trong vocabulary, chi con he so chan)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sentence", nargs="?")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if args.sentence:
        explain(args.sentence, out)
        return
    while True:
        sentence = input("\nGo mot cau tieng Anh (Enter de thoat): ").strip()
        if not sentence:
            return
        explain(sentence, out)


if __name__ == "__main__":
    main()
