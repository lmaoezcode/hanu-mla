# File của Ko: mô hình và đánh giá

**Khoảng 2 giờ, đọc sau file `00`.** Mỗi mục có bài tự làm, đáp án ở cuối. Hãy tự làm trước khi xem.

**Phần việc của Ko:**

- TF-IDF + Logistic Regression.
- Thước đo và so sánh.
- Controlled check.
- Ca lỗi của LR.

## 1. Biến chữ thành số: TF-IDF (25 phút)

Máy không đọc được chữ, nên phải biến mỗi câu thành một dãy số.

### Ý tưởng

Bạn lướt đề thi và thấy chữ "và" ở khắp nơi. Chữ đó không giúp đoán môn gì. Nhưng nếu thấy "enzyme" thì đoán ngay là sinh học. **Từ càng hiếm càng mang nhiều thông tin.**

IDF đo độ hiếm đó. Trong dự án:

| Từ | IDF | Ý nghĩa |
| --- | ---: | --- |
| `the` | 1,526 | Có ở rất nhiều câu |
| `was` | 3,288 | Khá phổ biến |
| `however` | 6,352 | Khá hiếm |
| `fish` | 6,547 | Khá hiếm |

Công thức trong code, với `n` là số câu train và `df` là số câu chứa từ đó:

```
IDF = ln((1 + n) / (1 + df)) + 1
```

Ví dụ: `the` có trong khoảng 4.240 trên 7.177 câu train.

### Cấu hình trong dự án

- **Từ đơn và cụm hai từ:** `have`, `two`, `have two`.
- **Chữ thường hóa:** `Here` thành `here`.
- **`sublinear_tf`:** từ lặp lại được tính giảm dần, `tf = 1 + ln(số lần)`.
- **Chuẩn hóa L2:** chia cho độ dài của vector để câu dài không tự có số lớn hơn.
- **Tối đa 30.000 đặc trưng,** chỉ học từ **train**.

### Chi tiết dễ bị hỏi: bộ tách từ

TF-IDF **bỏ từ 1 ký tự và dấu câu**. Với `I have two fish in a bowl .`:

```
Còn lại: have, two, fish, in, bowl, have two, two fish, fish in, in bowl
Có trong 30.000 đặc trưng: fish, have, have two, in, two
```

Vì vậy `I`, `a`, `.` không có tác dụng. Từ chưa có trong đặc trưng như `bowl` bị bỏ qua.

**Tự làm 1.** Đoán trước: bỏ dấu chấm ở câu `Here is the area where the computer was .` thì xác suất thay đổi thế nào?

**Tự làm 2.** Vì sao không được tính IDF từ cả dev và test?

## 2. Logistic Regression: bảng cộng trừ điểm (35 phút)

### Ý tưởng

Tưởng tượng có 6 bảng điểm, mỗi bảng cho một mức A1 đến C2. Mỗi từ cộng hoặc trừ điểm vào từng bảng. Mức nào điểm cao nhất thì thắng.

### Công thức cho mỗi mức

```
điểm = hệ số chặn + tổng(trọng số TF-IDF của từ × hệ số của từ)
```

- **Hệ số chặn:** điểm khởi đầu của mức đó.
- **Hệ số của từ:** máy học được. Dương là kéo về mức đó, âm là đẩy ra xa.

Ví dụ thật:

| Từ | A1 | A2 | B1 | B2 | C1 | C2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `there` | −0,62 | +4,40 | +1,09 | −1,08 | −1,99 | −1,80 |
| `however` | −0,15 | −0,78 | −0,46 | +0,05 | +0,71 | +0,63 |

### Từ điểm sang xác suất: softmax

Softmax biến điểm thành phần trăm, tổng bằng 100%:

```
xác suất của mức k = e^(điểm k) / tổng e^(điểm mọi mức)
```

### Lần theo câu đúng: `score_dev_0045`

`Here is the area where the computer was .`, đáp án **A2**.

Đóng góp vào điểm A2, hệ số chặn là +1,102:

| Đặc trưng | TF-IDF | Hệ số A2 | Đóng góp |
| --- | ---: | ---: | ---: |
| `was` | 0,176 | +3,65 | +0,642 |
| `here` | 0,366 | +1,64 | +0,599 |
| `area` | 0,282 | +1,75 | +0,494 |
| `where` | 0,270 | +1,21 | +0,326 |
| `area where` | 0,443 | +0,48 | +0,211 |
| `is the` | 0,255 | +0,56 | +0,142 |
| `is` | 0,133 | +0,47 | +0,063 |
| `the area` | 0,337 | +0,03 | +0,009 |
| `computer` | 0,374 | −0,08 | −0,028 |
| `where the` | 0,361 | −0,36 | −0,129 |
| `the` | 0,138 | −1,77 | −0,245 |
| **Tổng** | | | **+2,084** |

Điểm A2 = 1,102 + 2,084 = **3,186**.

| Mức | A1 | A2 | B1 | B2 | C1 | C2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Điểm | −3,292 | **3,186** | 2,232 | 0,788 | −0,391 | −2,523 |
| Xác suất | 0,001 | **0,663** | 0,255 | 0,060 | 0,019 | 0,002 |

LR đoán **A2**, trùng đáp án. Lưu ý từ `was` đẩy mạnh nhất, nghĩa là mô hình dựa vào từ, không hiểu nghĩa của câu.

### Lần theo câu sai: `score_dev_0002`

`I have two fish in a bowl .`, đáp án **A1**. Đóng góp vào điểm B1, hệ số chặn +1,320:

| Đặc trưng | TF-IDF | Hệ số B1 | Đóng góp |
| --- | ---: | ---: | ---: |
| `fish` | 0,541 | +1,09 | +0,588 |
| `in` | 0,181 | +0,63 | +0,114 |
| `have two` | 0,668 | +0,14 | +0,094 |
| `two` | 0,372 | −0,03 | −0,010 |
| `have` | 0,299 | −0,54 | −0,163 |

Điểm B1 = 1,320 + 0,624 = **1,944**, cao nhất trong 6 mức, xác suất 0,439. LR đoán B1, **lệch 2 bậc** so với A1.

### Vì sao mô hình phù hợp, và học thế nào

- **Vì sao hợp:** độ khó câu gắn nhiều với từ vựng. TF-IDF rất thưa, có 30.000 cột và mỗi câu chỉ dùng vài cột. LR xử lý tốt, nhanh, và xem được hệ số của từng từ.
- **Loss (log-loss):** phạt nặng khi mô hình rất tự tin mà sai. Máy chỉnh hệ số để giảm tổng mức phạt trên train.
- **Giả định:** các từ cộng điểm độc lập. Thứ tự từ chỉ được thấy qua cụm hai từ, và mô hình coi 6 mức là 6 lớp **không có thứ tự**.
- **`C = 10`:** núm chỉnh độ tự do. `C` lớn cho phép hệ số lớn hơn, dễ học thuộc hơn. Chọn bằng dev.
- **`class_weight="balanced"`:** nhân hệ số cho nhãn hiếm, như môn ít tín chỉ được tính nặng hơn. A1 hệ số 25,45, C2 13,14, B2 0,48.

**Tự làm 3.** Câu toàn từ lạ `xyzzy qwerty blorp` sẽ được đoán mức nào? Dùng bảng hệ số chặn: A1 −2,589, A2 1,102, B1 1,320, B2 1,117, C1 0,537, C2 −1,487.

**Tự làm 4.** Trong `score_dev_0045`, đổi `computer` thành `car`. Đoán trước, rồi chạy thử bằng `2_du_doan_mot_cau.bat`.

**Tự làm 5.** Một từ đóng góp +0,588. Điều đó có chứng minh từ này gây ra lỗi không?

## 3. Thước đo (30 phút)

### Ma trận nhầm lẫn của LR trên test

Hàng là đáp án thật, cột là mô hình đoán. Tổng theo cột là số lần đoán mức đó.

| Thật \\ Đoán | A1 | A2 | B1 | B2 | C1 | C2 | Tổng |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | 0 | 16 | 18 | 2 | 1 | 0 | 37 |
| A2 | 0 | **93** | 50 | 11 | 4 | 0 | 158 |
| B1 | 1 | 199 | **237** | 89 | 21 | 0 | 547 |
| B2 | 0 | 46 | 129 | **189** | 95 | 0 | 459 |
| C1 | 0 | 1 | 34 | 84 | **68** | 0 | 187 |
| C2 | 1 | 0 | 6 | 26 | 39 | **0** | 72 |
| Tổng đoán | 2 | 355 | 474 | 401 | 228 | 0 | 1.460 |

### Accuracy

```
(0 + 93 + 237 + 189 + 68 + 0) / 1460 = 587 / 1460 = 0,402
```

Vì sao không dùng làm thước đo chính? Dữ liệu lệch, và accuracy coi đoán A1 thành A2 giống hệt đoán A1 thành C2.

### Precision, recall, F1

Hình dung kiểm tra gian lận trong phòng thi:

- **Recall:** trong số người gian lận thật, bắt được bao nhiêu.
- **Precision:** trong số người bị bắt, bao nhiêu người gian lận thật.

Với mức A2:

```
recall    = 93 / 158 = 0,589
precision = 93 / 355 = 0,262
F1        = 2 × 0,262 × 0,589 / (0,262 + 0,589) = 0,363
```

LR hay đoán A2 quá tay: 355 lần, trong khi chỉ có 158 câu A2.

**Macro-F1:** trung bình F1 của 6 mức, các mức tính ngang nhau.

```
(0 + 0,363 + 0,464 + 0,440 + 0,328 + 0) / 6 = 0,266
```

### MAE

Trung bình số bậc lệch. Ví dụ 3 câu đáp án A1, A2, B1, mô hình đoán A1, A2, B2: lệch 0, 0, 1, vậy MAE = 1/3 = 0,33.

### QWK

Giống hai giám khảo chấm cùng bài. QWK hỏi: hai người đồng thuận hơn mức may rủi bao nhiêu, và lệch xa bị phạt theo **bình phương**?

```
QWK = 1 − (tổng lệch bình phương quan sát) / (tổng lệch bình phương nếu ghép ngẫu nhiên)
```

Tính tay. Đáp án A1, A2, B1 là `0, 1, 2`. Mô hình đoán `0, 1, 3`.

- **Quan sát:** 0² + 0² + 1² = 1.
- **Nếu ghép ngẫu nhiên:** lấy mỗi đáp án ghép với mọi dự đoán, cộng lại, chia 3.
    - Đáp án 0: 0, 1, 9. Tổng 10.
    - Đáp án 1: 1, 0, 4. Tổng 5.
    - Đáp án 2: 4, 1, 1. Tổng 6.
    - (10 + 5 + 6) / 3 = 7.
- **QWK** = 1 − 1/7 = **0,857**.

Đọc QWK: 1 là khớp hoàn toàn, 0 là không hơn may rủi, âm là tệ hơn may rủi.

### Khoảng tin cậy

QWK của LR trên test: 0,547, khoảng 95% từ 0,512 đến 0,577. Đây là độ dao động khi lấy mẫu lại **các câu test**. Nó không tính đến việc đổi seed huấn luyện hay đổi loại dữ liệu.

Dự án chưa có khoảng tin cậy cho **hiệu số** giữa hai mô hình. Chỉ nhìn hai khoảng có chồng nhau hay không thì chưa đủ để kết luận khi so sánh trực tiếp.

**Tự làm 6.** Tính recall và precision của B1.

**Tự làm 7.** Vì sao F1 của C2 bằng 0?

**Tự làm 8.** Tính MAE khi đáp án là A1, B1, C1 và mô hình đoán A2, B1, A2.

## 4. Đọc kết quả, kết luận đúng mức (15 phút)

| Mô hình | QWK | MAE | Macro-F1 |
| --- | ---: | ---: | ---: |
| Luôn đoán B2 | 0,000 | 0,894 | 0,080 |
| Cây AWL | 0,246 | 1,811 | 0,078 |
| TF-IDF + LR | 0,547 | 0,728 | 0,266 |

**Câu đơn giản:** trên cùng 1.460 câu test, LR tốt hơn hai mô hình kia ở QWK và MAE. Nhưng LR không đoán đúng câu A1 hay C2 nào, nên chưa dùng được để phát hiện câu ở hai đầu thang.

### Điểm tinh tế: QWK chung cao hơn QWK từng nguồn

| Phạm vi trên test | n | QWK | MAE |
| --- | ---: | ---: | ---: |
| SCoRE | 698 | 0,155 | 0,736 |
| Wiki-Auto | 762 | 0,360 | 0,720 |
| Chung | 1.460 | 0,547 | 0,728 |

QWK chung (0,547) cao hơn **cả hai** nguồn. Một cách giải thích hợp lý: câu SCoRE thường dễ, câu Wiki-Auto thường khó, nên chỉ cần tách được hai kiểu câu là QWK chung đã tăng. Đây là giả thuyết, chưa được chứng minh. Vì vậy **một phần** QWK có thể đến từ khác biệt nguồn, và không nên hiểu 0,547 hoàn toàn là khả năng nhận biết độ khó.

Giống như một lớp giỏi và một lớp yếu: cả trường có vẻ phân loại rất tốt, nhưng trong từng lớp thì phân loại kém hơn nhiều.

## 5. Controlled check và ca lỗi (20 phút)

Đọc phần 1, 3, 6 của file `03`.

Tập nói controlled check theo 5 bước:

| Bước | Nội dung |
| --- | --- |
| Câu hỏi | Lệch nguồn có làm LR yếu trên SCoRE không? |
| Giả định | Cân bằng trọng số hai nguồn sẽ cải thiện QWK và MAE trên SCoRE |
| Đổi gì | Chỉ thêm trọng số nguồn, giữ nguyên mọi thứ khác, chỉ chấm trên dev |
| Kết quả | Trên SCoRE: MAE 0,705 → 0,695, nhưng QWK 0,244 → 0,223. Wiki-Auto xấu đi |
| Quyết định | Giữ mô hình cũ. Đây là một cách thử, không chứng minh lệch nguồn vô hại |

Quy luật lỗi được số liệu dev ủng hộ: **kéo về mức giữa**. Câu ≤7 từ nhãn A1, A2: đoán cao 69/125, đoán thấp 2/125. Câu ≤7 từ nhãn từ B2 trở lên: đoán thấp 33/57, đoán cao 7/57.

Giả thuyết **chưa** đủ bằng chứng: lỗi đoán thấp ở C1, C2 do từ lạ (17,9% so với 16,2%, chênh lệch nhỏ).

Tập trung vào 3 ca:

- `score_dev_0002`: từ `fish`.
- `score_dev_0580`: từ `you` kéo câu dài xuống A2.
- `wiki_dev_0644`: `leukocytosis` có khó nhưng mô hình không tận dụng được.

**Tự làm 9.** Muốn kiểm tra giả thuyết "`you` kéo câu xuống", em làm thí nghiệm nhỏ nào?

**Tự làm 10.** Nếu chạy controlled check trên test rồi đổi mô hình theo kết quả, sai ở đâu?

## 6. Luyện nói (15 phút)

Tự nói thành tiếng, mỗi câu khoảng 1 phút, mở file bằng chứng tương ứng.

| Câu hỏi | Ý cần có | Mở file |
| --- | --- | --- |
| Với dòng đó, mô hình chính ra dự đoán thế nào? | TF-IDF, cộng điểm, softmax, nhãn cao nhất | `.bat` số 2 |
| Vì sao chọn TF-IDF + LR? | Hợp từ vựng, dữ liệu thưa, xem được hệ số; giới hạn về thứ tự từ | `lr_top_coefficients.csv` |
| Đổi tiền xử lý thì sao, kiểm tra thế nào? | Bỏ bigram hoặc đổi `C`, so trên dev, không dùng test | `validation_candidates.json` |
| Bằng chứng LR tốt hơn baseline? | Cùng tập test, QWK, MAE, kèm giới hạn A1, C2 | `test_metrics.csv` |
| Một ca lỗi? | Quan sát, giả thuyết chưa kiểm tra, bước tiếp theo | File `03` |
| Em tự kiểm tra được gì ngay bây giờ? | Tính recall từ ma trận, dò một câu | Giấy, `.bat` |

**Hai giới hạn nên tự nói được:** xác suất chưa hiệu chỉnh; QWK chung có thể chứa khác biệt nguồn.

## Đáp án

1. Không đổi: 0,663. TF-IDF bỏ dấu câu nên các đặc trưng giữ nguyên.
2. Vì như vậy thông tin từ đề thi lọt vào lúc ôn, là rò rỉ. Script verify đã kiểm tra IDF chỉ tính từ train.
3. Không có đặc trưng nào, chỉ còn hệ số chặn. B1 cao nhất (1,320) nên đoán **B1**, xác suất 0,317. B1 thắng do hệ số chặn, không phải vì câu đó giống B1.
4. Vẫn A2, xác suất tăng nhẹ lên 0,673. `computer` chỉ đóng góp −0,028 vào A2, nhưng khi đổi từ thì cụm hai từ và chuẩn hóa cũng đổi theo.
5. Không. Đó là mô hình đang dùng từ đó như thế nào, chưa phải nguyên nhân. Muốn kiểm tra thì đổi từ đó rồi xem dự đoán thay đổi ra sao.
6. Recall = 237/547 = 0,433. Precision = 237/474 = 0,500.
7. LR không đoán C2 lần nào, nên số đoán đúng C2 bằng 0.
8. Lệch 1, 0, 3. MAE = 4/3 = 1,33.
9. Đổi đúng một chỗ: thay `you` bằng `visitors` trong vài câu dev, so xác suất trước và sau. Ghi giả định trước khi chạy.
10. Đó là chọn mô hình bằng test. Khi đó test không còn khách quan, và điểm test không còn đại diện cho dữ liệu mới.
