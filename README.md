# MLA 2026 – CEFR Sentence Classification (Group 10, CLC02)

Phân loại độ khó CEFR (A1–C2) cho từng câu tiếng Anh với ba baseline: majority B2, AWL density tree, TF-IDF + Logistic Regression.

## Người mới bắt đầu ở đây

Mở [huong_dan/0_BAT_DAU_TU_DAY.pdf](huong_dan/0_BAT_DAU_TU_DAY.pdf). File này có lịch học và thứ tự đọc.

Có hai cách chạy code:

| Bạn đang có | Cách làm |
| --- | --- |
| Gói `MLA_nhom10.zip` (chỉ Windows 64-bit) | Không cần cài gì. Giải nén hết, rồi làm theo `0_BAT_DAU_TU_DAY.pdf` |
| Chỉ có code tải từ GitHub | Cần cài Python. Làm theo mục "Chạy thí nghiệm" bên dưới |

Gói zip khoảng 65 MB và **không có trên GitHub**, hãy xin nhóm. Các file `.bat` nhắc tới trong tài liệu học chỉ chạy được trong gói zip, vì gói có kèm sẵn Python. Bản trong `dong_goi/` không chạy được trực tiếp.

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

Các lệnh khác:

```bash
python scripts/show_results.py
python scripts/predict_sentence.py "Here is the area where the computer was ."
python scripts/run_dev_checks.py
```

Ba lệnh này lần lượt in bảng kết quả, giải thích dự đoán cho một câu, và chạy lại controlled check cùng phần chọn ca lỗi. Lệnh cuối chỉ dùng train và dev.
