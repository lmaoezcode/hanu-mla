# MLA 2026 – CEFR Sentence Classification (Group 10, CLC02)

Phân loại độ khó CEFR (A1–C2) cho từng câu tiếng Anh. Phạm vi hiện tại: mô hình mức câu với ba baseline (majority B2, AWL density tree, TF-IDF + Logistic Regression).

## Cấu trúc thư mục

```
data/         Dữ liệu gốc (CEFR-SP, Academic Word List)
scripts/      Script chạy thí nghiệm và dựng tài liệu/slide
output/
  experiments/sentence-baselines/   Kết quả baseline, mô hình, dự đoán
  docx/                             Tài liệu Word đã tạo
docs/
  PROJECT_OVERVIEW.md               Tổng quan dự án
  reference/                        Tài liệu đề bài, nhận xét của giảng viên
assets/       Hình ảnh dùng trong slide
requirements.txt
```

## Chạy lại thí nghiệm

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/fetch_awl.py
python scripts/run_sentence_baselines.py
python scripts/verify_sentence_baselines.py
```

## Dựng tài liệu

Các script `scripts/build_*.py` (cần `python-docx`) ghi vào `output/docx/`.
`scripts/build_midterm_deck.mjs` dựng slide giữa kỳ và phụ thuộc vào runtime presentation của Codex cài cục bộ (đường dẫn `SKILL_DIR`, `RUNTIME_PYTHON` cần chỉnh theo máy).

Xem thêm [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md).