"""Print the main results table from a saved run."""

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"majority": "Luon doan B2", "awl": "Cay AWL", "tfidf_lr": "TF-IDF + LR"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "experiments" / "sentence-baselines")
    out = parser.parse_args().output_dir
    with (out / "test_metrics.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    print(f"\n{'Mo hinh':<16}{'QWK':>8}{'MAE':>8}{'Macro-F1':>10}{'Accuracy':>10}")
    for row in rows:
        print(f"{NAMES[row['model']]:<16}{float(row['qwk']):>8.3f}{float(row['mae']):>8.3f}"
              f"{float(row['macro_f1']):>10.3f}{float(row['accuracy']):>10.3f}")
    print(f"\nThu muc: {out}\n")


if __name__ == "__main__":
    main()
