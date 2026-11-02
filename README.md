# MLA 2026 – CEFR Sentence Classification (Group 10, CLC02)

Phân loại độ khó CEFR (A1–C2) cho từng câu tiếng Anh với ba baseline: majority B2, AWL density tree, TF-IDF + Logistic Regression.

## Cấu trúc thư mục

```
data/           Dữ liệu gốc (CEFR-SP, Academic Word List)
scripts/        Script tải dữ liệu, chạy và kiểm tra thí nghiệm
requirements.txt
```

Thư mục `output/` được sinh ra khi chạy thí nghiệm và không được đưa lên Git.

## Chạy thí nghiệm

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/fetch_awl.py
python scripts/run_sentence_baselines.py
python scripts/verify_sentence_baselines.py
```
