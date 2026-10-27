# CEFR sentence baseline experiment

This folder contains an actual baseline run completed on 4 October 2026. The
task is six-class sentence classification, not passage CEFR assessment or text
rewriting. The intended application supports teachers reviewing sentences above
a teacher-specified class level.

## Results

| Model | Test QWK | Test MAE |
| --- | ---: | ---: |
| Always B2 | 0.000000 | 0.893836 |
| AWL density tree | 0.245683 | 1.810959 |
| TF-IDF plus Logistic Regression | 0.546598 | 0.728082 |

The LR model has no correct A1 or C2 predictions. Its macro-F1 is 0.265678.
AWL results are a negative finding for this selected implementation; the source
list is not a CEFR lexicon. The AWL tree was chosen by validation QWK; a competing
unweighted tree had lower validation MAE. This tradeoff is retained, not hidden
or changed after looking at test results.

## Inputs and target

- HF snapshot: `data/cefr-sp/cefr-sp.json`, all 10,004 rows.
- Official split snapshots: `data/cefr-sp/official/`, six TSV text files.
- AWL source PDFs: `data/awl/awl-families.pdf` and `awl-headwords.pdf`.
- Target is the higher of two expert labels, matching the HF labels in every row.
- Train 7,178 raw records, 7,177 after one identical B1 copy is removed.
- Validation 1,366; test 1,460. No exact normalized-text overlap across splits.
- Test support: A1 37, A2 158, B1 547, B2 459, C1 187, C2 72.

`data_audit.json` contains SHA-256 hashes and the verified source URLs. The raw
snapshots were copied from the previous audit into `data/` so they do not depend
on temporary files. No source record or test split is relabeled or removed.
The local snapshots are authoritative for reproducing this run; live links can
change. Initial corpus download dates and upstream revisions were not recorded,
so the manifest does not invent them. AWL download provenance is separately
stored in `data/awl/download-provenance.json`.

The 5-34 length range, mean 14.8 and median 14 count whitespace tokens, including
punctuation and numerals. The explicit alphabetic-word regex used for the AWL
denominator and EDA yields 2-31, mean 13.0 and median 12. Do not interchange these
counting conventions.

## Protocol

1. Extract full listed AWL forms; verify 570 headwords and 3,111 distinct forms.
2. Match the HF and official row multisets, retain both annotators and source
   licenses, remove the within-train duplicate and audit exact overlaps.
3. Fit majority, AWL density trees and TF-IDF/LR on train only.
4. Select by maximum validation QWK, then lower MAE, then higher macro-F1; exact
   ties keep the first predeclared grid entry. Freeze models and settings.
5. In a separate phase, evaluate the frozen models on test. Compute per-class
   and source reports, and 1,000 paired stratified bootstrap resamples.

QWK/MAE are the main metrics. Macro-F1 diagnoses imbalance. Accuracy is saved for
transparency, not used to select the models. Bootstrap intervals condition on
fixed fitted models and test class counts, not training variability or domain
shift. Majority intervals consequently collapse to the point values.

## Reproduce without overwriting the first run

Use Python 3.12 and a project-local environment containing
`requirements-baselines.txt`. From the project root, run:

```powershell
& '.\.venv-baselines\Scripts\python.exe' 'scripts\run_sentence_baselines.py' --phase select --output-dir 'output\experiments\sentence-baselines-reproduction'
& '.\.venv-baselines\Scripts\python.exe' 'scripts\run_sentence_baselines.py' --phase test --output-dir 'output\experiments\sentence-baselines-reproduction'
```

The script refuses to overwrite a frozen selection or test result. The `audit`
phase only refreshes data/provenance metadata and does not refit or select models.
The original experiment folder must not be used for iterative test tuning.
The seed is 20261004; package versions are recorded in `environment.json`.

## Output map

- `selection_plan.json`, `validation_candidates.json`, `frozen_selection.json`:
  declared search grid, validation scores and selected settings.
- `data_audit.json`, `audited_sentences.csv`, `eda_by_level.csv`: matched data,
  duplicates, source information and explicitly defined descriptive features.
- `awl_manifest.json`, `awl_forms.csv`, `awl_tree_rules.txt`: lexicon extraction
  and the selected density rules; displayed rules are rounded.
- `awl_density_tree.joblib`, `tfidf_lr.joblib`: the fitted models. Load only
  trusted local joblib artifacts.
- `test_results.json`, `test_metrics.csv`: full metrics, conditional confidence
  intervals and the three confusion matrices.
- `test_predictions.csv`: all 1,460 IDs, targets, both annotators, model
  predictions and probability vectors for the two learned models.
- `per_class_test.csv`, `per_source_test.csv`, `lr_top_coefficients.csv`: diagnostic
  reports. Per-source macro-F1 in the raw data always averages all six classes,
  including absent classes; compare it cautiously.
- `verification.json`: independent checks against saved test predictions.

## Limits and next work

The max-label target differs from the original paper's accept-either-annotator
evaluation, and Newsela is not included. These results are not directly
comparable to the paper's published scores. The official split addresses
sentence similarity, but no complete document-level leakage claim is made.
The training rarity feature means train document frequency at most five, not
general English rarity. The classification probabilities are not calibrated.

BiLSTM/GloVe, a teacher-facing interface and the approximately 30-sentence HANU
qualitative review remain future work. No classroom-usefulness claim is made.

## Sources and permissions

- [UniversalCEFR](https://huggingface.co/datasets/UniversalCEFR/cefr_sp_en)
- [CEFR-SP original files](https://github.com/yukiar/CEFR-SP/tree/main/CEFR-SP)
- [Arase, Uchida and Kajiwara 2022](https://aclanthology.org/2022.emnlp-main.416/)
- [Coxhead AWL full families](https://www.wgtn.ac.nz/lals/resources/academicwordlist/publications/awlsublists1.pdf)
- [scikit-learn 1.7 QWK](https://scikit-learn.org/1.7/modules/generated/sklearn.metrics.cohen_kappa_score.html)

HF lists CC BY-NC-SA 4.0; the original SCoRE source is CC BY-NC-SA 4.0 and
Wiki-Auto is CC BY-SA 3.0. Source metadata is retained, and use remains
non-commercial educational research. No open license is asserted for the AWL
PDFs; check permissions before redistributing source material.
