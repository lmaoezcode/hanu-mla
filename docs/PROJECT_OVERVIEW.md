# Tổng quan dự án MLA CEFR Sentence Classification

## 1. Mục tiêu của dự án

Dự án nghiên cứu bài toán phân loại độ khó của **từng câu tiếng Anh** theo sáu mức CEFR:

`A1 -> A2 -> B1 -> B2 -> C1 -> C2`

Người dùng mục tiêu là giáo viên tiếng Anh tại HANU muốn rà soát hoặc hạ độ khó của tài liệu đọc cho một lớp có trình độ CEFR đã biết. Công cụ dự kiến sẽ:

1. nhận một bài đọc do giáo viên cung cấp;
2. tách bài đọc thành các câu;
3. dự đoán nhãn CEFR và sáu xác suất cho từng câu;
4. đánh dấu những câu cao hơn trình độ mục tiêu của lớp;
5. để giáo viên quyết định giữ, sửa, thay hoặc kiểm tra thêm câu đó.

Phạm vi hiện tại chỉ là **mô hình mức câu**. Dự án không:

- gán một mức CEFR chung cho cả bài đọc;
- dùng phân vị 75 hoặc quy tắc khác để tổng hợp câu thành đoạn;
- tự động viết lại câu;
- thay thế quyết định của giáo viên;
- đánh giá hoặc chấm điểm người học.

## 2. Trạng thái hiện tại

Đã hoàn thành:

- kiểm tra và ghép bản UniversalCEFR với các split CEFR-SP gốc;
- giữ hai nhãn chuyên gia và metadata giấy phép;
- loại một bản sao hoàn toàn giống nhau trong tập train;
- kiểm tra không có câu trùng hoàn toàn giữa train, validation và test;
- tải và kiểm tra danh sách Academic Word List chính thức;
- chạy ba baseline: majority B2, AWL density tree và TF-IDF + Logistic Regression;
- chọn hyperparameter bằng validation trước khi mở test;
- đánh giá QWK, MAE, macro-F1, accuracy, từng lớp, từng nguồn và bootstrap CI;
- xác minh lại metric từ dự đoán đã lưu và kiểm tra TF-IDF chỉ học từ train;
- tạo proposal một trang và báo cáo kết quả baseline;
- tạo outline, script, Q&A, PowerPoint và PDF cho giai đoạn giữa kỳ.

Chưa hoàn thành:

- BiLSTM với GloVe;
- transformer nhỏ;
- API hoặc chương trình dự đoán dành cho người dùng;
- giao diện heatmap hoặc giao diện giáo viên;
- bộ tách câu cho bài đọc thực tế;
- kiểm tra định tính khoảng 30 câu HANU;
- calibration cho xác suất;
- đánh giá khả năng sử dụng trong lớp học.

Kết quả baseline đã đóng băng:

| Mô hình | Test QWK | Test MAE | Macro-F1 |
| --- | ---: | ---: | ---: |
| Luôn dự đoán B2 | 0.000000 | 0.893836 | 0.079729 |
| AWL density tree | 0.245683 | 1.810959 | 0.078400 |
| TF-IDF + Logistic Regression | 0.546598 | 0.728082 | 0.265678 |

TF-IDF + Logistic Regression là baseline tốt nhất hiện tại theo QWK và MAE, nhưng F1 của A1 và C2 đều bằng 0. AWL density có QWK dương nhưng MAE tệ hơn cả majority baseline, nên không thể coi AWL là một thang CEFR độc lập đáng tin cậy.

## 3. Kiến trúc tổng thể

Dự án có hai pipeline tương đối độc lập:

1. **Pipeline nghiên cứu ML**: dữ liệu -> audit -> tạo đặc trưng -> chọn mô hình -> test -> kiểm chứng -> báo cáo.
2. **Pipeline tạo tài liệu**: nội dung và kết quả -> DOCX/PPTX -> PDF/render -> kiểm tra trình bày.

```text
Nguồn CEFR-SP                  Nguồn AWL
  |                              |
  |                              +--> fetch_awl.py
  |                                     |
  v                                     v
data/cefr-sp/                    data/awl/*.pdf
  |                                     |
  +------------------+------------------+
                     |
                     v
          run_sentence_baselines.py
             phase select
                     |
          +----------+-----------+
          |                      |
     data audit            model selection
          |                      |
          +----------+-----------+
                     |
              frozen models
                     |
                     v
          run_sentence_baselines.py
               phase test
                     |
         predictions and metrics
                     |
          +----------+-----------+
          |                      |
          v                      v
verify_sentence_          build_teacher_
baselines.py              followup.py
          |                      |
          v                      v
verification.json       proposal and report DOCX
```

Các script tạo outline, script thuyết trình, Q&A và slide là nhánh artifact cũ hơn. Chúng không tham gia huấn luyện hoặc đánh giá mô hình.

## 4. Cấu trúc thư mục

```text
mla_project/
|-- AGENT.md                       # Tài liệu tổng quan này
|-- requirements-baselines.txt     # Phiên bản thư viện cho pipeline ML
|-- data/
|   |-- cefr-sp/
|   |   |-- cefr-sp.json           # Snapshot UniversalCEFR, 10,004 dòng
|   |   `-- official/              # 6 split TSV gốc của SCoRE/Wiki-Auto
|   `-- awl/
|       |-- awl-families.pdf       # Toàn bộ dạng từ AWL
|       |-- awl-headwords.pdf      # 570 headword và sublist
|       `-- download-provenance.json
|-- scripts/
|   |-- fetch_awl.py
|   |-- run_sentence_baselines.py
|   |-- verify_sentence_baselines.py
|   |-- build_teacher_followup.py
|   |-- build_student_outline.py
|   |-- build_revised_outline.py
|   |-- build_midterm_documents.py
|   |-- build_midterm_deck.mjs
|   |-- render_with_word.ps1
|   `-- export_pptx_to_pdf.ps1
|-- assets/
|   `-- teacher-reading-review.png
|-- MLA của Khoa/                   # Tài liệu gốc và phản hồi ban đầu
|-- output/
|   |-- experiments/sentence-baselines/
|   |-- docx/
|   |-- pptx/
|   `-- pdf/
`-- tmp/                            # Render và file trung gian, không phải đầu ra chuẩn
```

## 5. Dữ liệu và quy ước nhãn

### 5.1 UniversalCEFR

File: `data/cefr-sp/cefr-sp.json`

Mỗi record có các trường:

- `title`
- `lang`
- `source_name`
- `format`
- `category`
- `cefr_level`
- `license`
- `text`

Tổng số: 10,004 câu.

Phân bố nhãn:

| Lớp | Số câu |
| --- | ---: |
| A1 | 124 |
| A2 | 1,271 |
| B1 | 3,305 |
| B2 | 3,330 |
| C1 | 1,744 |
| C2 | 230 |

### 5.2 CEFR-SP gốc

Thư mục: `data/cefr-sp/official/`

Mỗi dòng TSV có dạng:

```text
sentence<TAB>label_by_annotator_1<TAB>label_by_annotator_2
```

Nhãn số `1..6` tương ứng với `A1..C2`.

Target dùng trong thí nghiệm hiện tại là:

```text
target = max(annotator_1, annotator_2)
```

Quy ước này khớp toàn bộ nhãn của snapshot UniversalCEFR. Nó không giống cách đánh giá của paper gốc, nơi dự đoán có thể được chấp nhận nếu khớp một trong hai annotator. Vì vậy không so sánh trực tiếp score hiện tại với score trong paper.

### 5.3 Split

| Split | Trước xử lý | Dùng trong thí nghiệm |
| --- | ---: | ---: |
| Train | 7,178 | 7,177 |
| Validation | 1,366 | 1,366 |
| Test | 1,460 | 1,460 |

Một câu B1 trùng hoàn toàn bên trong train bị loại. Không phát hiện câu trùng hoàn toàn giữa các split. Điều này không chứng minh không có document-level leakage, vì bản public không có document ID.

Test support:

| Lớp | Test n |
| --- | ---: |
| A1 | 37 |
| A2 | 158 |
| B1 | 547 |
| B2 | 459 |
| C1 | 187 |
| C2 | 72 |

### 5.4 Giấy phép

- Hugging Face ghi CC BY-NC-SA 4.0.
- SCoRE gốc: CC BY-NC-SA 4.0.
- Wiki-Auto gốc: CC BY-SA 3.0.
- AWL PDF không được dự án tự tuyên bố là open license; cần kiểm tra quyền trước khi phân phối lại.

Dự án hiện được giới hạn ở nghiên cứu giáo dục phi thương mại.

## 6. Pipeline thí nghiệm ML

Script chính: `scripts/run_sentence_baselines.py`

Script được chia thành ba phase để tránh vô tình dùng test cho model selection.

### 6.0 Thu thập AWL

Script: `scripts/fetch_awl.py`

`main` tải hai PDF AWL chính thức, kiểm tra response bắt đầu bằng header PDF, tính SHA-256, lưu kích thước, URL cuối và thời điểm tải vào `data/awl/download-provenance.json`. Script không ghi đè PDF đã tồn tại. Việc trích dạng từ và kiểm tra 570 family được thực hiện sau đó bởi `parse_awl` trong pipeline chính.

### 6.1 Phase audit

```powershell
& '.\.venv-baselines\Scripts\python.exe' `
  'scripts\run_sentence_baselines.py' `
  --phase audit
```

Chức năng:

- đọc hai PDF AWL;
- xác minh 570 family và 3,111 dạng từ khác nhau;
- đối chiếu multiset giữa UniversalCEFR và CEFR-SP gốc;
- giữ hai annotator, source và license;
- kiểm tra split count và exact overlap;
- đánh dấu bản sao trong train;
- tính length, AWL density và corpus-relative rare-word ratio;
- cập nhật audit metadata, không huấn luyện lại mô hình.

### 6.2 Phase select

```powershell
& '.\.venv-baselines\Scripts\python.exe' `
  'scripts\run_sentence_baselines.py' `
  --phase select `
  --output-dir 'output\experiments\sentence-baselines-reproduction'
```

Chức năng:

- fit các model chỉ trên train;
- chọn hyperparameter chỉ bằng validation;
- ghi toàn bộ candidate score;
- đóng băng model và cấu hình;
- không tính test score.

Script từ chối ghi đè khi output directory đã có `frozen_selection.json`. Muốn chạy lại phải dùng một thư mục output mới, không xóa hoặc sửa run gốc.

Quy tắc chọn:

1. QWK validation cao nhất;
2. nếu bằng nhau, MAE thấp hơn;
3. nếu vẫn bằng nhau, macro-F1 cao hơn;
4. nếu vẫn bằng nhau, giữ candidate xuất hiện trước trong grid.

### 6.3 Phase test

```powershell
& '.\.venv-baselines\Scripts\python.exe' `
  'scripts\run_sentence_baselines.py' `
  --phase test `
  --output-dir 'output\experiments\sentence-baselines-reproduction'
```

Chức năng:

- load model đã đóng băng;
- dự đoán test đúng một lần cho run đó;
- tính QWK, MAE, macro-F1 và accuracy;
- tạo confusion matrix và per-class report;
- tính kết quả riêng theo SCoRE/Wiki-Auto;
- lưu xác suất của model học được;
- tạo 1,000 paired stratified bootstrap samples cho CI 95%;
- từ chối chạy nếu `test_results.json` đã tồn tại.

## 7. Các baseline

### 7.1 Majority predictor

Luôn trả về B2, lớp phổ biến nhất trong train sau deduplication: 2,472/7,177 câu.

Mục đích là tạo một mức tối thiểu mà model học được phải vượt qua. Đây không phải model được fit.

### 7.2 AWL density tree

Đặc trưng duy nhất:

```text
AWL density = số word token khớp AWL / tổng alphabetic word token
```

Quy tắc token:

- lowercase;
- bỏ số và dấu câu;
- giữ contraction có dấu nháy và từ có gạch nối như một token;
- match chính xác với toàn bộ dạng từ liệt kê trong AWL;
- tính cả lần xuất hiện lặp lại;
- không stemming;
- không tự đoán thêm thành viên của word family.

Model là `DecisionTreeClassifier` một chiều. Grid có:

- `max_leaf_nodes`: 2, 3, 6;
- `min_samples_leaf`: 50, 100, 200;
- `class_weight`: `None`, `balanced`.

Cấu hình được chọn bằng validation QWK:

```text
max_leaf_nodes = 6
min_samples_leaf = 100
class_weight = balanced
```

Kết quả cho thấy AWL là đặc trưng học thuật, không phải ánh xạ CEFR. Cây học quy tắc không đơn điệu, không dự đoán A2 hoặc B1, và dự đoán A1 quá nhiều.

### 7.3 TF-IDF và Logistic Regression

Pipeline:

```text
sentence
  -> TfidfVectorizer
  -> multinomial LogisticRegression
  -> six-class probability vector
  -> argmax CEFR label
```

TF-IDF cố định:

- word unigram và bigram;
- lowercase;
- sublinear term frequency;
- L2 normalization mặc định;
- tối đa 30,000 features;
- không bỏ stop word;
- vocabulary và IDF chỉ fit trên train.

Grid:

- `C`: 0.1, 1.0, 10.0;
- `min_df`: 1, 2.

Logistic Regression:

- solver `lbfgs`;
- L2 regularization;
- balanced class weights tính từ train;
- tối đa 2,000 iterations;
- seed 20261004.

Cấu hình được chọn:

```text
C = 10
min_df = 1
features = 30,000
iterations to converge = 160
```

Lưu ý: xác suất đầu ra chưa được calibration, đặc biệt khi dùng class weighting. Không mô tả chúng là xác suất chắc chắn rằng mọi người học sẽ thấy câu khó.

## 8. Metric

### QWK

Quadratic Weighted Kappa đo mức đồng thuận sau khi điều chỉnh theo đồng thuận ngẫu nhiên, đồng thời phạt lỗi xa nhiều hơn lỗi gần. QWK phù hợp vì CEFR có thứ tự.

QWK là metric chính và càng cao càng tốt.

### MAE

Gán `A1=0, A2=1, ..., C2=5`, sau đó tính sai số bậc tuyệt đối trung bình.

MAE càng thấp càng tốt. Các bước số chỉ là quy ước đánh giá; không khẳng định khoảng cách năng lực A1-A2 bằng B2-C1.

### Macro-F1

Tính F1 riêng cho từng lớp rồi lấy trung bình không trọng số. Dùng để phát hiện model bỏ qua A1/C2.

Macro-F1 là metric chẩn đoán bổ sung trong bản gửi thầy, không cần trình bày ngang hàng với QWK và MAE ở mọi bảng chính.

### Accuracy

Được lưu để minh bạch và kiểm tra, nhưng không dùng làm metric chính hoặc tiêu chí chọn model vì dữ liệu mất cân bằng.

### Bootstrap CI

- 1,000 lần;
- stratified theo true label;
- dùng cùng row index giữa các model để so sánh paired;
- giữ cố định fitted model và class count của test.

CI này chỉ phản ánh biến động lấy mẫu trong test có class count cố định. Nó không bao phủ training-seed variance hoặc domain shift.

## 9. Chức năng trong `run_sentence_baselines.py`

| Hàm | Chức năng |
| --- | --- |
| `utc_now` | Tạo timestamp UTC ISO. |
| `write_json` | Ghi JSON UTF-8, không cho phép NaN. |
| `write_csv` | Ghi CSV UTF-8 có BOM để mở tốt trong Excel. |
| `sha256` | Tính checksum nguồn dữ liệu. |
| `normalized_text` | Chuẩn hóa khoảng trắng để đối chiếu và tìm duplicate. |
| `word_tokens` | Token hóa alphabetic words cho AWL và EDA. |
| `parse_awl` | Trích AWL forms từ PDF, kiểm tra family/sublist và tạo manifest. |
| `audit_data` | Ghép HF với official files, audit split/duplicate/license và tạo feature mô tả. |
| `metrics` | Tính QWK, MAE, macro-F1 và accuracy. |
| `selection_key` | Triển khai thứ tự ưu tiên khi chọn candidate. |
| `load_records` | Đọc lại audited CSV và ép kiểu cho phase test. |
| `select_models` | Fit/search/freeze majority, AWL tree và TF-IDF/LR. |
| `fast_bootstrap_metrics` | Tính QWK/MAE/macro-F1 nhanh từ confusion matrix. |
| `test_models` | Đánh giá model đã đóng băng, lưu predictions, CI và báo cáo. |
| `main` | Parse `--phase`, `--output-dir` và điều phối pipeline. |

## 10. Kiểm chứng độc lập

Script: `scripts/verify_sentence_baselines.py`

Chạy:

```powershell
& '.\.venv-baselines\Scripts\python.exe' `
  'scripts\verify_sentence_baselines.py'
```

Script kiểm tra:

- SHA-256 của bảy input files;
- số row audit, kept, train và test;
- ID test không trùng;
- test support;
- confusion matrix dựng lại từ `test_predictions.csv`;
- QWK, MAE và macro-F1 tính độc lập;
- per-class support, predicted count và F1;
- dự đoán và xác suất khi load lại model joblib;
- tổng xác suất bằng 1;
- toàn bộ 30,000 IDF khớp công thức fit từ 7,177 câu train.

Kết quả ghi vào `output/experiments/sentence-baselines/verification.json`.

Không load file `.joblib` từ nguồn không tin cậy vì định dạng này có thể thực thi mã trong lúc deserialize.

## 11. Output của thí nghiệm

Thư mục chuẩn: `output/experiments/sentence-baselines/`

| File | Nội dung |
| --- | --- |
| `README.md` | Mô tả chi tiết run, kết quả và cách tái lập. |
| `selection_plan.json` | Grid và protocol trước test. |
| `validation_candidates.json` | Score của tất cả candidate trên validation. |
| `frozen_selection.json` | Cấu hình được chọn và trạng thái test. |
| `data_audit.json` | Hash, split, overlap, duplicate, length và agreement. |
| `audited_sentences.csv` | Toàn bộ 10,004 record sau khi ghép metadata và feature. |
| `eda_by_level.csv` | Thống kê theo split và CEFR. |
| `awl_manifest.json` | Kiểm tra nguồn và định nghĩa AWL feature. |
| `awl_forms.csv` | 3,111 dạng từ được trích từ AWL. |
| `awl_tree_rules.txt` | Luật cây AWL đã fit. |
| `awl_density_tree.joblib` | Model AWL đã đóng băng. |
| `tfidf_lr.joblib` | Pipeline TF-IDF/LR đã đóng băng. |
| `lr_top_coefficients.csv` | 20 feature có coefficient lớn nhất cho mỗi lớp. |
| `test_predictions.csv` | 1,460 target, prediction và probability vector. |
| `test_results.json` | Metric đầy đủ, confusion matrices, CI, per-class/source. |
| `test_metrics.csv` | Bảng metric gọn. |
| `per_class_test.csv` | Precision/recall/F1/support từng lớp. |
| `per_source_test.csv` | Metric theo SCoRE và Wiki-Auto. |
| `environment.json` | Phiên bản Python và package. |
| `verification.json` | Kết quả kiểm tra độc lập. |

## 12. Pipeline tạo tài liệu

### `scripts/build_teacher_followup.py`

Đây là builder chính cho tài liệu sau phản hồi của giảng viên.

Input:

- `test_results.json`
- `frozen_selection.json`
- `data_audit.json`
- `eda_by_level.csv`
- file Word gốc dùng làm visual template.

Output:

- `output/docx/Group10_CLC02_one_page_proposal.docx`
- `output/docx/Group10_CLC02_sentence_baseline_results.docx`

Các hàm:

| Hàm | Chức năng |
| --- | --- |
| `load_json` | Đọc kết quả thí nghiệm. |
| `style_setup` | Cấu hình style Word đen trắng. |
| `plain_doc` | Tạo document theo template gốc, A4, bố cục đơn giản. |
| `paragraph` | Thêm paragraph với spacing tùy chọn. |
| `heading` | Thêm Heading 1 và giữ cùng nội dung tiếp theo. |
| `hyperlink` | Tạo hyperlink OOXML màu đen có gạch chân. |
| `plain_table` | Tạo bảng không tô màu, viền xám, header lặp lại. |
| `page` | Chèn page break và heading đầu trang. |
| `proposal` | Tạo proposal một trang, sáu phần và bảng QWK/MAE. |
| `baseline_report` | Tạo báo cáo baseline, EDA, hạn chế và next work. |
| `main` | Kiểm tra trạng thái run rồi tạo cả hai DOCX. |

### `scripts/build_student_outline.py`

Tạo `MLA-2026-revised-outline-simple.docx` theo phong cách outline sinh viên đơn giản. Nội dung này được tạo trước khi có baseline thực tế nên không phải tài liệu kết quả mới nhất.

| Hàm | Chức năng |
| --- | --- |
| `remove_child_if_present` | Xóa shading hoặc border OOXML khỏi style khi có. |
| `configure_style` | Đặt Calibri, cỡ chữ, màu đen, spacing và alignment. |
| `add_outline_line` | Tạo một dòng outline có nhãn in đậm và nội dung thường. |
| `add_heading` | Thêm Heading 1 và giữ heading với đoạn sau. |
| `add_reference` | Thêm một nguồn tham khảo dạng văn bản đơn giản. |
| `build_document` | Sao cấu trúc visual từ file gốc, thay nội dung và lưu outline. |

### `scripts/build_revised_outline.py`

Tạo `MLA-2026-revised-outline.docx`, bản outline nhiều cấu trúc và chi tiết hơn. Đây là builder cũ; phần metric và wording có thể không phản ánh đầy đủ quyết định mới nhất.

Các helper `set_cell_shading`, `set_cell_margins`, `set_cell_width`, `prevent_row_split`, `set_repeat_table_header` và `set_table_borders` thao tác trực tiếp OOXML để ổn định bảng. `add_table`, `add_labeled_paragraph` và `add_bullet` tạo thành phần nội dung. `add_page_number`, `set_run_font` và `style_document` quản lý style, footer và page field. `build_document` ghép toàn bộ outline và ghi DOCX.

### `scripts/build_midterm_documents.py`

Tạo:

- script thuyết trình;
- file Q&A mức độ vừa phải.

Nội dung được lưu trong các cấu trúc `SCRIPT_SECTIONS` và `QNA_GROUPS`, sau đó render thành DOCX.

Các hàm `set_cell_shading`, `set_cell_borders`, `set_cell_margins` và `set_repeat_table_header` định dạng bảng; `set_run_font`, `clear_style_paragraph_decoration` và `configure_document` quản lý typography; `add_title` và `add_label_paragraph` tạo component; `build_script_document` tạo kịch bản; `build_qna_document` tạo Q&A; `main` tạo cả hai file.

### `scripts/build_midterm_deck.mjs`

Tạo PowerPoint 7 slide bằng `@oai/artifact-tool`:

- helper `addText` thêm textbox;
- `addSlideTitle` tạo tiêu đề slide;
- `setBackground` đặt nền;
- `addSourceNote` ghi script và nguồn vào speaker notes;
- xuất PNG nháp từng slide;
- xuất candidate PPTX;
- chạy finalizer kiểm tra số slide, font, native table/chart và hình học layout;
- tạo `output/pptx/MLA-2026-midterm-presentation.pptx`.

Script này chứa absolute path đến workspace và Codex runtime nên không portable sang máy khác nếu chưa sửa các constant đầu file.

### `scripts/render_with_word.ps1`

Mở DOCX ở chế độ read-only bằng Microsoft Word COM, export PDF rồi đóng Word trong `finally`. Dùng để render kiểm tra khi LibreOffice không có sẵn.

### `scripts/export_pptx_to_pdf.ps1`

Mở PPTX bằng PowerPoint COM, export PDF rồi đóng PowerPoint trong `finally`.

## 13. Các tài liệu đầu ra quan trọng

Mới nhất:

- `output/docx/Group10_CLC02_one_page_proposal.docx`
- `output/docx/Group10_CLC02_sentence_baseline_results.docx`
- `output/experiments/sentence-baselines/README.md`

Tài liệu giữa kỳ cũ:

- `output/docx/MLA-2026-revised-outline-simple.docx`
- `output/docx/MLA-2026-revised-outline.docx`
- `output/docx/MLA-2026-midterm-presentation-script.docx`
- `output/docx/MLA-2026-midterm-qna.docx`
- `output/pptx/MLA-2026-midterm-presentation.pptx`
- `output/pdf/MLA-2026-midterm-presentation.pdf`

Không dùng file trong `tmp/` làm deliverable. Đây là render, preview hoặc dữ liệu trung gian.

## 14. Môi trường và dependency

Pipeline baseline dùng Python 3.12 và các phiên bản trong `requirements-baselines.txt`:

```text
scikit-learn==1.7.2
numpy==2.5.3
scipy==1.18.1
joblib==1.6.0
threadpoolctl==3.7.0
cloudpickle==3.1.2
pypdf==6.7.1
```

Các builder DOCX cần `python-docx`. Builder slide cần Node.js, `@oai/artifact-tool` và các helper của presentations skill trong Codex runtime. Export DOCX/PPTX sang PDF cần Microsoft Word/PowerPoint trên Windows.

Thí nghiệm gốc dùng environment `.venv-baselines`. Không thêm package ML vào Python của document runtime.

## 15. Cách tái lập an toàn

1. Không thay đổi hoặc ghi đè `output/experiments/sentence-baselines/`.
2. Tạo một output directory mới cho reproduction.
3. Chạy phase `select`.
4. Đọc `validation_candidates.json` và `frozen_selection.json`.
5. Chỉ sau khi selection đã đóng băng mới chạy phase `test`.
6. Chạy `verify_sentence_baselines.py` cho run chuẩn; nếu muốn kiểm tra run khác, cần bổ sung tham số output cho verifier trước.
7. Không điều chỉnh model dựa trên test error rồi báo lại cùng test score như một đánh giá độc lập.

Run gốc dùng seed `20261004`. Hash nguồn nằm trong `data_audit.json`; phiên bản package nằm trong `environment.json`.

## 16. Các bất biến phải giữ

Khi sửa hoặc mở rộng dự án:

- input model vẫn là một câu tiếng Anh độc lập;
- output model vẫn là sáu probability và một nhãn A1-C2;
- không gộp C1/C2 thành `Advanced`;
- giữ thứ tự nhãn `A1, A2, B1, B2, C1, C2` ở mọi nơi;
- tokenizer, vocabulary và IDF không được fit trên validation/test;
- hyperparameter chỉ chọn bằng validation;
- test chỉ dùng sau khi cấu hình đóng băng;
- baseline majority tách biệt khỏi các classifier học được;
- AWL không được mô tả là CEFR vocabulary list;
- không suy CEFR của passage từ kết quả mức câu nếu chưa có dữ liệu kiểm chứng;
- báo QWK và MAE là metric chính;
- báo support và per-class result để không che lỗi A1/C2;
- macro-F1 là chẩn đoán mất cân bằng; accuracy chỉ là số bổ sung;
- không mô tả probability chưa calibration là confidence tuyệt đối;
- giữ teacher-in-the-loop và nêu rõ hạn chế domain shift;
- không tuyên bố HANU audit hoặc classroom validation đã hoàn thành khi chưa thực hiện;
- giữ metadata và yêu cầu giấy phép theo nguồn;
- không load model joblib không rõ nguồn;
- không sửa hoặc xóa run gốc để làm đẹp kết quả.

## 17. Hạn chế kỹ thuật hiện tại

- Chưa có package/module Python chuẩn; các script dùng constant và file path trực tiếp.
- Một số builder cũ hardcode absolute Windows paths.
- Chưa có automated test framework; verifier là script kiểm tra tích hợp.
- Chưa có CLI inference riêng cho một câu hoặc một file văn bản.
- Chưa có sentence segmentation component.
- Chưa có API schema, model registry hoặc deployment configuration.
- Chưa có calibration và threshold policy cho thao tác “highlight above class level”.
- Chưa có run BiLSTM nên chưa kiểm chứng giả thuyết word order.
- Source distribution khác mạnh giữa các lớp; pooled metric có thể chứa source signal.
- A1/C2 quá ít, và LR hiện không phân loại đúng hai lớp này trên test.
- AWL tree tối ưu theo QWK có MAE validation xấu; đây là tradeoff đã ghi nhận.
- Public data không đủ để tuyên bố không có document-level leakage.

## 18. Hướng phát triển đề xuất

Ưu tiên hợp lý tiếp theo:

1. chuyển logic audit và metric thành module có unit tests;
2. thêm CLI inference dùng model đã chọn mà không đụng vào test pipeline;
3. huấn luyện BiLSTM/GloVe với cùng split, target và protocol;
4. đánh giá nhiều seed cho neural model;
5. calibration xác suất bằng validation nếu giao diện cần uncertainty;
6. xây sentence segmentation và teacher-specified target-level rule;
7. thực hiện audit khoảng 30 câu HANU, gồm cả false negative;
8. chỉ sau đó mới xây heatmap/giao diện giáo viên;
9. giữ passage aggregation ngoài phạm vi cho đến khi có passage-level labels.

## 19. Nguồn chính

- UniversalCEFR: https://huggingface.co/datasets/UniversalCEFR/cefr_sp_en
- CEFR-SP repository: https://github.com/yukiar/CEFR-SP/tree/main/CEFR-SP
- Arase, Uchida and Kajiwara 2022: https://aclanthology.org/2022.emnlp-main.416/
- Academic Word List: https://www.wgtn.ac.nz/lals/resources/academicwordlist
- scikit-learn 1.7 documentation: https://scikit-learn.org/1.7/
