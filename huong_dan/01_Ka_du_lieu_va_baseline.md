# File của Ka: dữ liệu và baseline

**Khoảng 2 giờ, đọc sau file `00`.** Mỗi mục có bài tự làm, đáp án ở cuối. Hãy tự làm trước khi xem.

**Phần việc của Ka:**

- Kiểm tra dữ liệu, nhãn, chia tập.
- Baseline majority và cây AWL.
- Ca bất đồng nhãn, ca cây AWL sai.
- Chạy lại và kiểm chứng kết quả.

## 1. Một dòng dữ liệu là gì (15 phút)

Mỗi dòng trong file gốc `data/cefr-sp/official/score_dev.txt` có 3 cột:

```
Câu <TAB> nhãn người 1 <TAB> nhãn người 2
```

Nhãn số 1 đến 6 ứng với A1 đến C2. Ví dụ câu ở dòng 45 có ID `score_dev_0045`:

```
Here is the area where the computer was .    2    2
```

Cả hai chuyên gia đều cho mức 2, tức A2.

- **Đơn vị quan sát:** một câu. Không phải một người, cũng không phải một bài đọc.
- **Số dòng:** 10.004 câu trong dữ liệu gốc, dùng 10.003 câu sau khi bỏ một câu trùng.
- **Không có mã bài gốc:** không biết hai câu có cùng một bài hay không.

### Nhãn được tạo thế nào

Giống hai thầy cùng chấm một bài rồi lấy **điểm cao hơn**:

```
nhãn đích = max(người 1, người 2)
```

Ví dụ `score_dev_0163`, `Emma wanted a pink car .`, được gán A1 và A2, nên nhãn đích là **A2**.

Nhãn chỉ đo **ý kiến chuyên gia về độ khó**. Nhãn không đo việc sinh viên Việt Nam có thấy câu đó khó hay không.

Hai chuyên gia trùng nhau hoàn toàn ở 41,4% số câu. Các câu còn lại lệch đúng 1 bậc. Bộ dữ liệu công khai đã lọc các câu lệch xa hơn, nên 41,4% **không phải** mức đồng thuận thô ban đầu.

### Lúc dự đoán biết gì

| Thông tin | Có lúc dự đoán? | Được dùng làm đặc trưng? |
| --- | --- | --- |
| Chữ của câu | Có | Có |
| Mật độ AWL (tính từ chữ) | Có | Có |
| Nhãn của hai chuyên gia | Không | Không, đó là đáp án |
| Nguồn câu SCoRE hay Wiki | Câu mới thì không biết | Không, chỉ dùng để phân tích |

**Tự làm 1.** Câu có nhãn A1 và A2 thì đích là gì? Nếu đổi sang lấy `min` thì sao?

## 2. Chia tập (15 phút)

| Tập | Dùng | Số câu | SCoRE | Wiki-Auto | % SCoRE |
| --- | --- | ---: | ---: | ---: | ---: |
| Train | Học | 7.177 | 1.188 | 5.989 | 16,6% |
| Dev | Chọn cấu hình | 1.366 | 665 | 701 | 48,7% |
| Test | Chấm cuối | 1.460 | 698 | 762 | 47,8% |

Vẽ được sơ đồ này ra giấy:

```
Train → học mô hình và IDF
Dev   → chọn cấu hình tốt nhất → đóng băng
Test  → chấm một lần
```

**Đã kiểm tra trong `data_audit.json`:**

- Không có câu nào trùng hoàn toàn giữa ba tập.
- Bỏ 1 câu trùng trong train: `wiki_train_1907`.
- Dữ liệu Hugging Face khớp với file gốc.

**Chưa chứng minh được:** không rò rỉ ở mức bài gốc. Hai câu gần giống nhau hoặc cùng một bài vẫn có thể nằm ở hai tập, vì không có mã bài.

### Rủi ro dữ liệu quan trọng nhất: lệch nguồn

Hãy tưởng tượng bạn ôn thi chủ yếu bằng sách lịch sử, nhưng đề thi có một nửa là truyện tranh. Điểm có thể tụt không phải vì bạn kém, mà vì hai nguồn khác kiểu.

Dự án gặp đúng chuyện đó:

- SCoRE chiếm 16,6% train nhưng gần 50% dev và test.
- Câu A1 trong train: 41/47 câu từ Wiki-Auto. Câu A1 trong test: 33/37 câu từ SCoRE.
- Đặc trưng A1 mạnh nhất của LR là `died on` và `died`, từ những câu tiểu sử kiểu Wikipedia.

Đây là **giả thuyết hợp lý**, chưa phải nguyên nhân đã chứng minh. Controlled check trong file `03` đã thử và chưa cho thấy cân bằng trọng số là đủ.

Một rủi ro khác: A1 và C2 quá ít. Trong train A1 có 47 câu, C2 có 91 câu. Trong test A1 có 37 câu, C2 có 72 câu.

**Tự làm 2.** Tính % SCoRE của test từ bảng trên.

**Tự làm 3.** Nếu thầy nói: "Giả sử thay bằng câu trong sách giáo khoa Việt Nam thì sao?", em trả lời thế nào?

## 3. Baseline majority (15 phút)

Đây là cách khoanh toàn C. Mức phổ biến nhất trong train là B2 (2.472/7.177), nên câu nào cũng đoán **B2**.

Bảng số câu test:

| A1 | A2 | B1 | B2 | C1 | C2 | Tổng |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 37 | 158 | 547 | 459 | 187 | 72 | 1.460 |

**Accuracy:** số câu đúng chia tổng số câu. Chỉ câu B2 là đúng.

```
459 / 1460 = 0,314
```

**MAE:** gán A1=0, A2=1, B1=2, B2=3, C1=4, C2=5. Mỗi nhóm lệch khỏi B2 bao nhiêu bậc:

| Nhóm | Số câu | Lệch | Tổng lệch |
| --- | ---: | ---: | ---: |
| A1 | 37 | 3 | 111 |
| A2 | 158 | 2 | 316 |
| B1 | 547 | 1 | 547 |
| B2 | 459 | 0 | 0 |
| C1 | 187 | 1 | 187 |
| C2 | 72 | 2 | 144 |
| **Tổng** | 1.460 | | **1.305** |

```
1305 / 1460 = 0,894
```

**QWK = 0:** câu nào cũng đoán một mức, nên không phân biệt được câu dễ với câu khó.

**Baseline kiểm tra gì?** Nó trả lời: học từ dữ liệu có hơn việc chỉ biết mức nào phổ biến không?

**Tự làm 4.** Nếu mức phổ biến nhất là B1 thì accuracy trên test là bao nhiêu?

## 4. Đặc trưng AWL và cây quyết định (30 phút)

### Mật độ AWL

AWL là danh sách từ hay gặp trong văn bản học thuật, như `analysis`, `area`, `computer`.

```
mật độ AWL = số từ thuộc AWL / tổng số từ
```

Ví dụ `Here is the area where the computer was .`:

```
here, is, the, area, where, the, computer, was → 8 từ
area, computer → 2 từ AWL
mật độ = 2 / 8 = 0,25
```

Dấu câu không được tính là từ.

### Cây quyết định giống trò đoán 20 câu hỏi

Mỗi bước hỏi có hoặc không, đi dần tới câu trả lời. Cây này chỉ hỏi về một con số. Rút gọn từ `awl_tree_rules.txt`:

| Mật độ AWL | Cây đoán |
| --- | --- |
| Từ 0 đến 0,017241 | A1 |
| Trên 0,017241 đến 0,048810 | C2 |
| Trên 0,048810 đến 0,270979 | C1 |
| Trên 0,270979 | B2 |

Dò câu trên: 0,25 lớn hơn 0,048810 và nhỏ hơn 0,270979, nên ra **C1**. Đáp án là A2, nên cây sai.

Cây dễ dò bằng tay nên là **mô hình tham chiếu dễ diễn giải**. Đó là lý do nên giữ nó trong so sánh, dù kết quả kém.

### Cây học thế nào

Cây thử nhiều ngưỡng trên train. Mỗi lần chọn ngưỡng tách các nhóm sao cho mỗi nhóm "thuần" một nhãn nhất. Đó là tiêu chí Gini. Không cần nhớ công thức, chỉ cần nhớ ý này.

### Vì sao cây tệ

**Lý do 1: đặc trưng không đo đúng thứ cần đo.** AWL đo từ học thuật, không đo CEFR. Mật độ trung bình trong train tăng tới B2 rồi lại giảm:

| Mức | A1 | A2 | B1 | B2 | C1 | C2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Mật độ TB (%) | 1,1 | 2,1 | 5,7 | 7,5 | 7,5 | 5,7 |
| Không có từ AWL (%) | 93,6 | 85,0 | 54,3 | 37,2 | 34,8 | 45,1 |

Gần một nửa câu C2 không có từ AWL nào. Một lý do có thể là từ khó của chúng thường là thuật ngữ chuyên ngành, như các ca trong file `03`.

**Lý do 2: trọng số `balanced`.** Giống như nhân hệ số cho môn ít tín chỉ để không bị bỏ qua. A1 rất hiếm nên hệ số tới 25,45. Cây vì thế rất muốn đoán A1: trên test đoán A1 cho **836/1.460 câu**, trong khi chỉ có 37 câu A1 thật.

**Lý do 3: chọn theo QWK.** Luật chọn đã định trước là QWK cao nhất trên dev:

| Cây trên dev | QWK | MAE | Được chọn? |
| --- | ---: | ---: | --- |
| 6 lá, `balanced` | 0,228 | 1,863 | Có |
| 2 lá, không trọng số | 0,224 | 0,769 | Không |

Hơn 0,004 QWK nhưng MAE tệ gấp đôi. Nhóm **không đổi lại sau khi xem test**, vì như vậy là dùng test để chọn mô hình.

### Lỗi thật trong đặc trưng

Khi trích PDF, từ "acknowledgement**s**" bị xuống dòng nên chữ `s` thành một "từ AWL". Vì câu dữ liệu viết `It 's`, chữ `s` bị đếm.

- `It 's 10 p. m.`: 1/4 = 0,25 → cây đoán C1, đáp án A1.
- Chữ `s` khớp ở 73/1.366 câu dev. Bỏ nó đi thì dự đoán đổi ở 55 câu dev.

Kết quả đã đóng băng vẫn giữ nguyên và phải nêu đây là giới hạn. Muốn sửa thì làm một thí nghiệm mới.

**Tự làm 5.** Dò cây: câu 16 từ có 2 từ AWL.

**Tự làm 6.** Dò cây: câu không có từ AWL nào.

**Tự làm 7.** Vì sao "cây tệ" không có nghĩa là "AWL vô dụng"?

## 5. Đọc ca và chạy kiểm chứng (20 phút)

Mở phần 4, 5, 6 của file `03`. Đọc từng ca. Tập nói một ca theo khuôn:

```
ID → câu → nhãn → dự đoán → bằng chứng → giải thích → còn chưa chắc gì
```

Tập trung vào 3 ca:

- `score_dev_0163`: lấy max hay min làm đổi đáp án.
- `score_dev_0009`: lỗi chữ `s`.
- `wiki_dev_0476`: "ventriloquism" khó nhưng không thuộc AWL.

Số liệu của nhóm "không có từ AWL" trên dev: 829 câu đều bị đoán A1, chỉ 38 câu thật là A1, và 306 câu thật từ B2 trở lên.

### Kiểm chứng làm gì

Bấm `1_kiem_tra_ket_qua.bat`. Script này:

- So SHA-256 của 7 file dữ liệu để chắc chúng không đổi. Giống như đối chiếu mã niêm phong.
- Tính lại QWK, MAE, F1 từ các dự đoán đã lưu.
- Nạp lại mô hình, xem có ra đúng dự đoán đã lưu không.
- Kiểm tra IDF chỉ tính từ 7.177 câu train, tức không rò rỉ từ dev hay test.

Thấy `"all_passed": true` là đạt. Thông tin chi tiết nằm trong `verification.json`.

## 6. Suy luận khi thầy đổi điều kiện (10 phút)

**Tự làm 8.** Lấy `min` thay vì `max` làm nhãn. Phân bố thay đổi thế nào? Điểm có so sánh được không?

| Nhãn | A1 | A2 | B1 | B2 | C1 | C2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Lấy max (toàn bộ) | 124 | 1.271 | 3.305 | 3.330 | 1.744 | 230 |
| Lấy min (toàn bộ) | 672 | 2.427 | 3.704 | 2.534 | 634 | 33 |

**Tự làm 9.** Thầy thêm một từ học thuật vào câu `score_dev_0045`, thành 9 từ, 3 từ AWL. Cây đoán gì?

**Tự làm 10.** Nếu mô hình được dùng cho học sinh cấp 2, em có kết luận được gì từ kết quả này không?

## 7. Luyện nói (15 phút)

Tự nói thành tiếng, mỗi câu khoảng 1 phút, mở file bằng chứng tương ứng.

| Câu hỏi | Ý cần có | Mở file |
| --- | --- | --- |
| Chọn một dòng. Nhãn đo gì, lúc dự đoán biết gì, nhóm nào phải tách riêng? | Một câu, max hai nhãn, chỉ có chữ, không có mã bài | `audited_sentences.csv` |
| Baseline đoán gì cho dòng đó? | B2, vì sao | `frozen_selection.json` |
| Chọn một giả định. Đổi đi thì sao, kiểm tra thế nào? | max/min, hoặc bỏ `balanced`, so trên dev | `validation_candidates.json` |
| Một kết quả so với baseline? | Cây QWK hơn nhưng MAE tệ hơn majority | `test_metrics.csv` |
| Một ca bất đồng nhãn? | Quan sát, giả thuyết, bước tiếp theo | File `03` |
| Em tự kiểm tra được gì ngay bây giờ? | Tính MAE majority, dò cây, chạy verify | Giấy, `.bat` |

**Hai giới hạn nên tự nói được:** nhãn là ý kiến của chuyên gia và lấy max; không có mã bài nên không loại trừ được rò rỉ mức bài.

## Đáp án

1. Đích là A2. Lấy `min` thì là A1.
2. 698 / 1460 = 47,8%.
3. Kết quả hiện tại chưa nói được gì về nhóm đó, vì dữ liệu không có câu sách giáo khoa Việt Nam. Có thể kiểm tra bằng một mẫu câu có nhãn từ giáo viên.
4. 547 / 1460 = 0,375.
5. 2/16 = 0,125 → C1.
6. Mật độ 0 → A1.
7. Kết quả phụ thuộc cách làm: chỉ dùng một đặc trưng, dùng `balanced`, chọn theo QWK, có lỗi chữ `s`. AWL có thể vẫn hữu ích khi kết hợp với đặc trưng khác.
8. Phân bố dịch về phía dễ: A1 tăng từ 124 lên 672, C2 giảm từ 230 còn 33. C2 càng hiếm. Vì đáp án đã đổi, không được so trực tiếp điểm giữa hai cách. Muốn biết phải huấn luyện và chấm lại theo nhãn mới.
9. 3/9 = 0,333, lớn hơn 0,270979 → B2.
10. Không kết luận được. Dữ liệu không được thu thập từ nhóm này, và nhãn là ý kiến chuyên gia, không phải phản ứng của học sinh.
