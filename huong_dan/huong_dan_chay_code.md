# Hướng dẫn chạy code cho thầy xem

Không cần cài gì và không cần mạng. Gói này chỉ chạy trên **Windows 64-bit**.

## 1. Chuẩn bị

1. Giải nén toàn bộ file zip vào một thư mục **đường dẫn ngắn**, ví dụ `D:\MLA`. **Đừng chạy trực tiếp bên trong file zip.**
2. Bấm đúp `1_kiem_tra_ket_qua.bat`. Thấy `all_passed` là `true` tức là máy chạy được.

Nếu Windows hiện "Windows protected your PC", chọn **More info** rồi **Run anyway**.

## 2. Ba file để bấm

| File | Khi nào dùng | Mất khoảng |
| --- | --- | ---: |
| `1_kiem_tra_ket_qua.bat` | Chứng minh bảng kết quả khớp với dự đoán đã lưu | Dưới 30 giây |
| `2_du_doan_mot_cau.bat` | Thầy đưa một câu, hoặc đổi một từ để xem dự đoán | Vài giây |
| `3_chay_lai_tu_dau.bat` | Thầy muốn xem chạy lại toàn bộ | 30 giây đến vài phút |

## 3. Kết quả phải thấy

| Mô hình | QWK | MAE |
| --- | ---: | ---: |
| Luôn đoán B2 | 0,000 | 0,894 |
| Cây AWL | 0,246 | 1,811 |
| TF-IDF + LR | 0,547 | 0,728 |

## 4. Mở gì cho thầy xem

Trong `output\experiments\sentence-baselines\`:

| File | Cho thấy |
| --- | --- |
| `test_metrics.csv` | Bảng điểm chính |
| `test_predictions.csv` | Dự đoán từng câu; tìm theo ID bằng Ctrl+F |
| `audited_sentences.csv` | Toàn bộ câu, nhãn, đặc trưng |
| `awl_tree_rules.txt` | Luật của cây |
| `verification.json` | Kết quả kiểm chứng |

Trong `output\experiments\dev-checks\`: controlled check và các ca đã chọn. Giải thích nằm trong file `03` của thư mục `huong_dan`.

## 5. Chạy lại code

Bấm `3_chay_lai_tu_dau.bat`. File này tự tạo một thư mục mới, ví dụ `output\experiments\lan-1`, rồi chạy select, test và verify. Kết quả gốc không bị đổi.

Muốn gõ tay, mở cửa sổ lệnh tại thư mục gói code:

```
python\python.exe scripts\run_sentence_baselines.py --phase select --output-dir output\experiments\lan-2
python\python.exe scripts\run_sentence_baselines.py --phase test --output-dir output\experiments\lan-2
python\python.exe scripts\verify_sentence_baselines.py --output-dir output\experiments\lan-2
```

Lần chạy lại dùng cùng dữ liệu, cùng cấu hình, cùng seed, nên phải ra cùng bảng điểm. Chạy lại **không** làm tập test thành "chưa từng thấy".

## 6. Khi gặp lỗi

| Thấy gì | Nghĩa là | Làm gì |
| --- | --- | --- |
| `A frozen selection already exists` | Thư mục này đã có kết quả. Code cố ý từ chối ghi đè | Không phải lỗi. Dùng thư mục mới |
| `Test results already exist` | Tương tự, cho bước test | Không phải lỗi. Dùng thư mục mới |
| `Experiment outputs must stay inside the project directory` | `--output-dir` nằm ngoài thư mục gói code | Dùng đường dẫn trong `output\experiments\` |
| `.bat` mở lên rồi tắt ngay, hoặc báo thiếu file | Chưa giải nén hết hoặc đang chạy trong zip | Giải nén lại |
| `The filename or extension is too long` | Đường dẫn thư mục quá dài | Chuyển gói code về thư mục ngắn như `D:\MLA` |
| Không chạy được trên máy | Có thể thiếu quyền hoặc máy không phải Windows 64-bit | Báo thầy, mở các file kết quả và PDF rồi tính trên giấy |
