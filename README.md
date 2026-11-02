# MLA 2026 – CEFR Sentence Classification (Group 10, CLC02)

Phân loại độ khó CEFR (A1–C2) cho từng câu tiếng Anh với ba baseline: majority B2, AWL density tree, TF-IDF + Logistic Regression.

## Người mới bắt đầu ở đây

Mở [huong_dan/0_BAT_DAU_TU_DAY.pdf](huong_dan/0_BAT_DAU_TU_DAY.pdf). File này có lịch học và thứ tự đọc.

## Cấu trúc thư mục

```
data/           Dữ liệu gốc (CEFR-SP, Academic Word List)
scripts/        Script tải dữ liệu, chạy và kiểm tra thí nghiệm
output/         Kết quả đã lưu của thí nghiệm
huong_dan/      Tài liệu học cho thành viên mới
dong_goi/       File dùng để tạo gói chạy trên Windows
requirements.txt
```

## Chạy thí nghiệm

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/verify_sentence_baselines.py
```

Lệnh trên kiểm tra kết quả đã lưu trong `output/experiments/sentence-baselines/`.

Muốn chạy lại từ đầu, dùng một thư mục mới vì script từ chối ghi đè kết quả cũ:

```bash
python scripts/run_sentence_baselines.py --phase select --output-dir output/experiments/lan-2
python scripts/run_sentence_baselines.py --phase test --output-dir output/experiments/lan-2
python scripts/verify_sentence_baselines.py --output-dir output/experiments/lan-2
```
