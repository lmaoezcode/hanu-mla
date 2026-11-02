# File chung cho Ka và Ko

**Cả hai đọc file này trước, khoảng 1 giờ.** Đọc từ trên xuống, chưa cần nhớ hết. Sau đó Ka đọc file `3_Ka`, Ko đọc file `3_Ko`.

## 1. Dự án trong một trang

**Câu chuyện:** cô giáo tiếng Anh ở HANU có một bài đọc cho lớp B1. Cô muốn biết câu nào có thể khó hơn trình độ lớp để sửa hoặc thay.

**Công cụ làm gì:** đọc **một câu tiếng Anh**, đoán câu đó thuộc mức nào trong sáu mức.

```
A1 → A2 → B1 → B2 → C1 → C2
dễ nhất                khó nhất
```

- **Đầu vào:** chỉ chữ của một câu.
- **Đầu ra:** một nhãn và 6 xác suất.
- **Người quyết định:** giáo viên. Công cụ chỉ gợi ý.
- **Không làm:** không chấm cả bài đọc, không tự viết lại câu.

**Tiến độ thật:**

| Đã có | Chưa có |
| --- | --- |
| Kiểm tra dữ liệu, 3 mô hình, kết quả test | Báo cáo cuối |
| Chạy lại và kiểm chứng tự động | Khoảng tin cậy cho hiệu số giữa hai mô hình |
| Controlled check và bảng ca lỗi (AI soạn) | BiLSTM, giao diện cho giáo viên, thử với giáo viên thật |

## 2. Machine Learning là gì

**Lập trình thường:** bạn viết luật cho máy. Ví dụ: "điểm dưới 4 thì trượt môn."

**Machine Learning:** bạn đưa ví dụ có đáp án, máy tự tìm luật. Giống như xem 100 câu đã có đáp án rồi tự rút kinh nghiệm cách làm bài.

Bốn từ phải nhớ:

| Từ | Nghĩa | Trong dự án |
| --- | --- | --- |
| Mẫu (sample) | Một ví dụ | Một câu tiếng Anh |
| Nhãn (label) | Đáp án | A1 đến C2, do chuyên gia gán |
| Đặc trưng (feature) | Con số mô tả mẫu, vì máy chỉ làm việc được với số | Mật độ từ học thuật, trọng số của từng từ |
| Mô hình (model) | Luật máy học được | Cây quyết định, Logistic Regression |

### Ba tập dữ liệu giống ba loại đề

| Tập | Số câu | Giống như | Dùng để |
| --- | ---: | --- | --- |
| Train | 7.177 | Đề cương có đáp án | Máy học |
| Dev | 1.366 | Đề thi thử | Chọn cấu hình tốt nhất |
| Test | 1.460 | Đề thi thật | Chấm cuối cùng |

<figure><svg viewBox="0 0 680 150" width="100%" role="img" aria-label="Sơ đồ chia train, dev, test" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Arial, sans-serif"><g stroke="#17365d"><rect x="2" y="26" width="478" height="44" fill="#dbe5f3"/><rect x="480" y="26" width="91" height="44" fill="#fff6e0"/><rect x="571" y="26" width="107" height="44" fill="#f7dfd9"/></g><g font-size="13" font-weight="600" fill="#17365d" text-anchor="middle"><text x="241" y="53">Train: 7.177 câu</text><text x="525" y="53">Dev: 1.366</text><text x="624" y="53">Test: 1.460</text></g><g font-size="12" fill="#333" text-anchor="middle"><text x="241" y="16">Đề cương có đáp án</text><text x="525" y="16">Đề thi thử</text><text x="624" y="16">Đề thi thật</text><text x="241" y="92">Máy học từ đây; IDF cũng chỉ tính ở đây</text><text x="525" y="92">Chọn cấu hình</text><text x="624" y="92">Chấm cuối</text><text x="525" y="108">rồi đóng băng</text><text x="624" y="108">sau khi chốt</text></g><text x="340" y="138" font-size="12" fill="#333" text-anchor="middle">Thứ tự: học trên train → chọn trên dev → đóng băng → chấm trên test. Không chỉnh mô hình theo điểm test.</text></svg></figure>

**Vì sao không gộp lại?** Nếu thi đúng câu đã có trong đề cương, điểm cao chưa chắc đã giỏi. Có thể chỉ là học thuộc. Hiện tượng này gọi là **overfitting** (học thuộc đề cũ, gặp đề mới thì dở). Nếu đề thi lọt vào lúc ôn thì gọi là **rò rỉ** (leakage).

**Tập test đã dùng thế nào:** nhóm chọn xong và đóng băng mô hình bằng dev, rồi mới chấm test. Code từ chối chạy test lần hai trong cùng thư mục. Chạy lại ở thư mục khác cũng không làm test thành "chưa từng thấy", và không được chỉnh mô hình dựa trên điểm test.

### Baseline là gì

Baseline là mốc so sánh đơn giản. Một bài trắc nghiệm mà khoanh bừa toàn C đã được 25%. Nếu bạn ôn cả tuần mà được 26%, bạn chưa giỏi lên bao nhiêu. Vì vậy điểm của mô hình chỉ có nghĩa khi so với mốc.

## 3. Ba mô hình trên một câu thật

Câu mẫu: **`score_dev_0045`**: `Here is the area where the computer was .`, nhãn đúng **A2**. Câu này thuộc tập dev, mô hình chưa học nó.

| Mô hình | Cách nghĩ | Đoán | Đúng? |
| --- | --- | --- | --- |
| Majority | Khoanh toàn một đáp án phổ biến nhất trong train | B2 | Sai |
| Cây AWL | Đếm từ học thuật: `area`, `computer` là 2/8 = 0,25 | C1 | Sai |
| TF-IDF + LR | Cộng trừ điểm cho từng từ | A2 (66,3%) | Đúng |

Chuỗi xử lý (pipeline):

<figure><svg viewBox="0 0 680 150" width="100%" role="img" aria-label="Sơ đồ pipeline từ câu đến nhãn" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Arial, sans-serif"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8z" fill="#17365d"/></marker></defs><g fill="#e8edf4" stroke="#17365d"><rect x="2" y="10" width="92" height="46" rx="5"/><rect x="118" y="10" width="92" height="46" rx="5"/><rect x="234" y="10" width="92" height="46" rx="5"/><rect x="350" y="10" width="92" height="46" rx="5"/><rect x="466" y="10" width="92" height="46" rx="5"/><rect x="582" y="10" width="92" height="46" rx="5"/></g><g font-size="13" font-weight="600" fill="#17365d" text-anchor="middle"><text x="48" y="38">Câu</text><text x="164" y="38">Tách từ</text><text x="280" y="38">Đặc trưng</text><text x="396" y="38">Mô hình</text><text x="512" y="38">6 xác suất</text><text x="628" y="38">Nhãn</text></g><g stroke="#17365d" stroke-width="1.5" marker-end="url(#a)"><line x1="94" y1="33" x2="117" y2="33"/><line x1="210" y1="33" x2="233" y2="33"/><line x1="326" y1="33" x2="349" y2="33"/><line x1="442" y1="33" x2="465" y2="33"/><line x1="558" y1="33" x2="581" y2="33"/></g><g font-size="11" fill="#333" text-anchor="middle"><text x="48" y="78">Here is the</text><text x="48" y="93">area where...</text><text x="164" y="78">here, is, the,</text><text x="164" y="93">area, where...</text><text x="280" y="78">area 0,282</text><text x="280" y="93">was 0,176</text><text x="396" y="78">TF-IDF + LR</text><text x="396" y="93">cộng trừ điểm</text><text x="512" y="78">A2 66,3%</text><text x="512" y="93">B1 25,5% ...</text><text x="628" y="78">Đoán A2</text><text x="628" y="93">Đáp án A2: đúng</text></g><text x="340" y="130" font-size="12" fill="#333" text-anchor="middle">Ví dụ thật: câu score_dev_0045 đi qua từng bước</text></svg></figure>

Thử ngay: mở `2_du_doan_mot_cau.bat`, gõ câu trên, xem có ra đúng bảng này không.

## 4. Kết quả chính

Cả ba mô hình chấm trên cùng 1.460 câu test.

| Mô hình | QWK (cao tốt) | MAE (thấp tốt) | Macro-F1 (cao tốt) | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| Luôn đoán B2 | 0,000 | 0,894 | 0,080 | 31,4% |
| Cây AWL | 0,246 | 1,811 | 0,078 | 10,3% |
| **TF-IDF + LR** | **0,547** | **0,728** | **0,266** | **40,2%** |

- **QWK:** mức đồng thuận với chuyên gia, lệch càng xa phạt càng nặng. Bằng 0 là không hơn đoán theo may rủi, gần 1 là rất khớp.
- **MAE:** trung bình lệch bao nhiêu bậc. 0,728 là lệch chưa đến một bậc.
- **Macro-F1:** điểm trung bình của 6 mức, các mức tính ngang nhau, nên mức hiếm như A1, C2 không bị bỏ qua.
- **Accuracy:** tỉ lệ đoán trúng chính xác.

**Được phép nói:**

- Trên cùng tập test, LR tốt hơn hai mô hình còn lại theo QWK và MAE.
- LR vẫn yếu: không đoán đúng câu A1 hay C2 nào trên test.
- Mô hình mới được đánh giá ở mức câu.

**Không được nói:**

- "Mô hình đã dùng được trong lớp học." Chưa thử với giáo viên thật.
- "AWL vô dụng." Chỉ kết luận được về cách cài đặt này.
- "Xác suất 66% nghĩa là chắc chắn 66%." Xác suất chưa được hiệu chỉnh.
- So trực tiếp với điểm của bài báo gốc. Cách lấy nhãn khác nhau.

## 5. Buổi phỏng vấn kiểm tra gì

Mỗi người khoảng 6–8 phút, điểm riêng, tối đa 30.

| Tiêu chí | Điểm | Thầy muốn thấy |
| --- | ---: | --- |
| Dữ liệu và nhãn | 8 | Mở một câu có ID. Một dòng là gì, nhãn từ đâu, lúc dự đoán biết gì, chia tập ra sao, một rủi ro |
| Lý do chọn mô hình | 8 | Từ đặc trưng đến dự đoán. Baseline để làm gì. Nếu đổi điều kiện thì sao |
| Đánh giá và kết quả | 8 | So với baseline, đọc một thước đo, một ca lỗi, một giới hạn, tập test đã dùng thế nào |
| Đóng góp và kiểm tra thực hành | 6 | Làm hoặc dò một bước nhỏ, tính một thước đo nhỏ, đoán đầu vào đổi thì sao |

**Quy định cần nhớ:**

- Được mở tài liệu và code của mình. **Bạn bè và AI không được nhắc** khi đang phỏng vấn.
- Được trả lời bằng tiếng Việt, được viết hoặc vẽ.
- Thầy sẽ đổi ví dụ, nên học thuộc không đủ. Hãy hiểu **cách dò**.
- "Em chưa đủ bằng chứng để khẳng định, nhưng có thể kiểm tra bằng cách..." là câu trả lời được tính.
- Không cần huấn luyện lại trên lớp. Thầy có thể dùng kết quả đã lưu.

Mỗi tiêu chí chấm 0, 4, 6 hoặc 8 (tiêu chí cuối: 0, 3, 4,5 hoặc 6). Chỉ đọc thuật ngữ thì được khoảng mức 4. Giải thích đúng một câu thật được mức 6. Nối được các bước và suy luận khi điều kiện đổi được mức 8.

## 6. Bảng phân công lý tưởng

Đây là cách chia việc lý tưởng cho dự án, **không phải nhật ký** những việc đã diễn ra. Tên file trong cột "Sản phẩm" là kết quả chạy code; file riêng của mỗi bạn sẽ giải thích dần. Từ nào chưa rõ thì tra mục từ điển ở dưới.

| Hạng mục | Phụ trách | Sản phẩm | Xong khi |
| --- | --- | --- | --- |
| Kiểm tra dữ liệu, nhãn, chia tập | Ka | `data_audit.json`, `eda_by_level.csv` | Giải thích được một dòng thật và một rủi ro dữ liệu |
| Baseline majority, cây AWL | Ka | `awl_tree_rules.txt`, `frozen_selection.json` | Tự dò cây bằng tay trên một câu |
| Ca bất đồng nhãn, ca cây AWL sai | Ka | Phần 4, 5 của file `4_bang_ca_loi` | Đọc và nói được bằng chứng từng ca |
| Chạy lại và kiểm chứng kết quả | Ka | `verification.json` | Chạy verify và đọc được kết quả |
| TF-IDF + LR | Ko | `tfidf_lr.joblib`, `lr_top_coefficients.csv` | Lần theo được một câu ra dự đoán |
| Thước đo và so sánh | Ko | `test_metrics.csv`, `per_class_test.csv` | Tính tay được một thước đo nhỏ |
| Controlled check | Ko | `output/experiments/dev-checks/` | Nói được giả định, kết quả, quyết định |
| Ca lỗi của LR | Ko | Phần 3 của file `4_bang_ca_loi` | Đọc và nói được bằng chứng từng ca |
| Kết luận và giới hạn | Cả hai | Mục kết luận của báo cáo | Mỗi người tự nói được một giới hạn |

Bảng ca lỗi và controlled check do AI soạn. Nếu thầy hỏi ai làm, hãy trả lời đúng như vậy.

## 7. Tự kiểm tra

1. Một dòng dữ liệu là gì? Mô hình được thấy gì lúc dự đoán?
2. Vì sao cần cả dev lẫn test?
3. Với câu bất kỳ, baseline đoán gì? Vì sao?
4. Tại sao accuracy của LR chỉ 40% mà MAE dưới 1?

## 8. Dùng AI thế nào cho đúng

AI giống một bạn học giỏi nhưng đôi lúc nói sai rất tự tin. Được nhờ giải thích, nhưng không được chép đáp án rồi coi là của mình.

| Nên | Không nên |
| --- | --- |
| Nhờ giải thích khái niệm, rồi tự giải thích lại bằng một câu thật | Nộp phần giải thích của AI như thể tự làm |
| Nhờ tìm lỗi code, rồi chạy lại để xác nhận | Tin con số AI nói mà không đối chiếu file kết quả |
| Ghi rõ đã dùng công cụ gì, vào việc gì, kiểm tra thế nào | Dùng AI để nhắc khi đang phỏng vấn |

**Công khai AI trong dự án này:** Claude (AI) đã soạn bảng ca lỗi, controlled check và các file học. Cách kiểm tra: chạy lại code, tính lại số liệu từ file kết quả đã lưu. Phần giải thích ca lỗi là suy luận, chưa phải nguyên nhân đã chứng minh.

## 9. Từ điển nhanh

| Thuật ngữ | Nghĩa |
| --- | --- |
| CEFR | Thang trình độ ngoại ngữ A1–C2 |
| Baseline, majority | Mốc so sánh đơn giản; majority là luôn đoán mức phổ biến nhất |
| TF-IDF | Cách biến câu thành số: từ càng hiếm càng được tính nặng |
| Logistic Regression (LR) | Mô hình cộng trừ điểm cho từng từ rồi đổi thành xác suất |
| Cây quyết định | Mô hình hỏi có hoặc không theo từng bước |
| Verify | Script tự kiểm tra lại kết quả đã lưu |
| SCoRE, Wiki-Auto | Hai nguồn câu: câu ví dụ cho người học, và câu Wikipedia |
| AWL | Academic Word List, danh sách từ học thuật. Không phải thang CEFR |
| Siêu tham số | Núm chỉnh do người chọn, ví dụ số lá của cây |
| Đóng băng | Chốt mô hình lại trước khi chấm test |
| Seed | Số cố định để phần ngẫu nhiên lặp lại y hệt |
| Ma trận nhầm lẫn | Bảng cho biết đáp án thật nào bị đoán thành mức nào |
| Controlled check | Đổi đúng một yếu tố để kiểm tra một giả thuyết |
| Bootstrap | Rút lại mẫu nhiều lần để xem con số dao động bao nhiêu |

## 10. Mang theo khi phỏng vấn

- Laptop đã giải nén gói code, đã bấm thử cả 3 file `.bat`.
- File `2_chung_Ka_Ko`, file của mình, file `4_bang_ca_loi`.
- Giấy bút để tính tay và vẽ.
- **Nếu máy hỏng:** báo thầy ngay, dùng PDF này và tính trên giấy. Rubric cho phép dùng kết quả đã lưu hoặc kiểm tra tương đương.

## Đáp án tự kiểm tra

1. Một câu tiếng Anh. Lúc dự đoán chỉ thấy chữ của câu, không thấy nhãn của chuyên gia.
2. Dev dùng để chọn cấu hình. Sau khi chọn, dev không còn khách quan nữa, nên cần test chưa dùng để chấm cuối.
3. Luôn là B2, vì B2 phổ biến nhất trong train (2.472/7.177 câu).
4. Đoán trúng chính xác chỉ 40%, nhưng đa số câu sai chỉ lệch một bậc nên trung bình lệch dưới 1.
