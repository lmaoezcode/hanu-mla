# Bảng ca lỗi và controlled check

> **Toàn bộ phần giải thích trong file này do AI soạn.** Số liệu lấy từ code chạy thật, nhưng các giải thích chỉ là suy luận từ bằng chứng, chưa phải nguyên nhân đã được chứng minh.

Tái tạo bằng lệnh: `python scripts/run_dev_checks.py`. Lệnh này chỉ dùng train và dev, không đọc tập test, không đổi mô hình đã đóng băng.

File bằng chứng trong `output/experiments/dev-checks/`:

- `controlled_source_check.csv`, `controlled_source_check.json`
- `selected_cases.csv`
- `hypothesis_checks.json`

## Phần 1. Controlled check: ảnh hưởng của nguồn câu

| Mục | Nội dung |
| --- | --- |
| Câu hỏi | Tỉ lệ nguồn lệch có làm LR yếu trên câu SCoRE không? SCoRE chiếm 16,6% train nhưng 48,7% dev. |
| Giả định trước khi chạy | Cân bằng trọng số hai nguồn sẽ cải thiện QWK và MAE trên SCoRE, có thể làm giảm ở Wiki-Auto. |
| Thay đổi duy nhất | Thêm trọng số để tổng trọng số của SCoRE và Wiki-Auto bằng nhau khi huấn luyện. |
| Giữ nguyên | `C=10`, `min_df=1`, từ đơn và cụm hai từ, 30.000 đặc trưng, seed 20261004, cùng tập train và dev. |
| Kiểm tra phụ | Huấn luyện lại không đổi gì thì ra đúng dự đoán của mô hình đã đóng băng trên dev. |

| Phạm vi trên dev | n | QWK gốc | QWK cân bằng | MAE gốc | MAE cân bằng | Macro-F1 gốc | Macro-F1 cân bằng |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Tất cả | 1.366 | 0,623 | 0,605 | 0,693 | 0,719 | 0,315 | 0,315 |
| SCoRE | 665 | 0,244 | 0,223 | 0,705 | 0,695 | 0,194 | 0,213 |
| Wiki-Auto | 701 | 0,483 | 0,441 | 0,680 | 0,742 | 0,363 | 0,373 |

**Đọc kết quả:**

- Giả định **chỉ đúng một phần**. Trên SCoRE, MAE tốt hơn một chút (0,705 → 0,695) và macro-F1 tăng, nhưng QWK lại giảm (0,244 → 0,223).
- Wiki-Auto xấu đi rõ ở MAE (0,680 → 0,742).
- Tính chung, thước đo chính đều không tốt hơn.

**Quyết định:** giữ nguyên mô hình đã đóng băng. Thay đổi này không đủ để tăng độ tin cậy trên SCoRE.

**Không được kết luận:** "lệch nguồn không gây vấn đề". Đây chỉ là một cách cân bằng, trên một tập dev. Chưa thử huấn luyện riêng từng nguồn, và không có khoảng tin cậy cho các chênh lệch này.

## Phần 2. Quy tắc chọn ca

Chọn ngẫu nhiên với seed cố định, sắp theo ID trước khi chọn, trải đều theo nhãn thật. Không chọn tay. Chạy lại ra đúng các ca này.

| Nhóm | Kho ca trên dev | Số ca mỗi nhãn | Số ca chọn |
| --- | ---: | ---: | ---: |
| Lỗi LR lệch từ 2 bậc | 127 | Tối đa 2 | 12 |
| Hai người gán nhãn bất đồng | 863 | Tối đa 1 | 5 |
| Cây AWL lệch từ 2 bậc | 861 | Tối đa 1 | 6 |

## Phần 3. Ca lỗi của LR (phần của Ko)

Nhãn đích là mức cao hơn trong hai nhãn của chuyên gia.

| ID | Câu | Hai nhãn | Đích | LR | Bằng chứng | Giải thích (AI soạn) |
| --- | --- | --- | --- | --- | --- | --- |
| `score_dev_0002` | I have two fish in a bowl . | A1, A1 | A1 | B1 | `fish` +0,59 | Từ chủ đề đẩy về B1, dù ngữ pháp rất đơn giản. |
| `score_dev_0008` | A monkey climbed on my shoulders . | A1, A1 | A1 | B1 | `monkey` +0,69, `my` +0,41 | Tương tự: từ cụ thể về động vật kéo mức lên. |
| `score_dev_0084` | Can I have a nickel ? | A2, A2 | A2 | B2 | `can` +0,62, `can have` +0,28 | Do "I" và "a" bị bỏ, câu còn lại thành "can have", một mẫu từ không thật sự có trong câu. |
| `score_dev_0169` | No birds live in that forest . | A2, A2 | A2 | B2 | `live` +0,35, `forest` +0,24, `birds` +0,24 | Nhiều từ về tự nhiên cộng lại. Có thể mô hình học từ Wiki-Auto rằng chủ đề này thuộc mức cao hơn. |
| `wiki_dev_0054` | The innovation that led to flatbread pizza was the use of tomato as a topping . | B1, B1 | B1 | C1 | `of` +0,60, `led` +0,31 | Câu dài, kiểu Wikipedia. "of" là tín hiệu về văn phong chứ không phải độ khó của từ. |
| `wiki_dev_0143` | Facilities for visitors around the lake include camping areas , picnic areas , toilets and barbecues . | B1, B1 | B1 | C1 | `and` +0,66, `around` +0,44 | Danh sách dài có "and" làm câu trông phức tạp, dù cấu trúc đơn giản. |
| `score_dev_0580` | It is a wonderful tourist spot where you can see the dolphins swim along the coast of Australia . | B1, B2 | B2 | A2 | `you` +0,77, `see` +0,43 | Từ "you" gắn với A2, kéo cả câu 18 từ xuống. Mô hình không thấy cấu trúc mệnh đề. |
| `wiki_dev_0363` | There are many other variations on male masturbation techniques . | B2, B2 | B2 | A2 | `there` +0,86, `there are` +0,21 | Mở đầu "there are" rất mạnh về A2 và lấn át các từ khó. |
| `wiki_dev_0494` | Not every poison has an antidote . | B2, C1 | C1 | A2 | `every` +0,64, `has` +0,37 | Câu ngắn, từ khó "antidote" không đủ sức. Chuyên gia cũng bất đồng ở câu này. |
| `wiki_dev_0559` | During an instrumental interlude , the music creates a thunder storm to indicate the passage of time . | B2, C1 | C1 | B1 | `thunder` +0,58, `music` +0,37 | Từ quen về chủ đề âm nhạc, thời tiết kéo xuống. Hình ảnh ẩn dụ không nằm trong đặc trưng. |
| `wiki_dev_0644` | An increase in the number of white blood cells in circulation is called leukocytosis . | C1, C2 | C2 | B2 | `the number` +0,35, `increase` +0,32 | LR không bao giờ đoán C2 trên test và chỉ có 91 câu C2 để học. Thuật ngữ y khoa khó không giúp được. |
| `wiki_dev_0690` | Hummingbirds are specialized nectarivores and are tied to the ornithophilous flowers upon which they feed . | C1, C2 | C2 | B2 | `and` +0,34, `specialized` +0,22 | Các từ khó nhất là từ hiếm, mô hình gần như không dùng được. Câu bị kéo về mức giữa. |

## Phần 4. Ca bất đồng nhãn (phần của Ka)

| ID | Câu | Hai nhãn | Đích | LR | Cây | Giải thích (AI soạn) |
| --- | --- | --- | --- | --- | --- | --- |
| `score_dev_0163` | Emma wanted a pink car . | A1, A2 | A2 | B1 | A1 | Lấy max nên đích là A2. Nếu lấy min, cây sẽ đúng. Điểm số phụ thuộc vào quy ước nhãn. |
| `wiki_dev_0073` | Mammals are set out by size with largest at the top . | A2, B1 | B1 | B2 | A1 | Từ quen nhưng cấu trúc "set out by" khó hơn. Bất đồng ở đây dễ hiểu. |
| `wiki_dev_0174` | English - language anime forums adopted those Japanese-style emoticons ... | B2, B1 | B2 | B1 | C2 | LR trùng nhãn của người thứ hai nhưng vẫn tính là sai vì đích là max. |
| `score_dev_0662` | Those women are Russian gymnasts . | B2, C1 | C1 | B1 | A1 | Câu 5 từ mà nhãn đến B2, C1, trông bất ngờ. Nên cân nhắc khả năng nhãn không ổn định, nhưng không đủ cơ sở nói nhãn sai. |
| `wiki_dev_0669` | It can sometimes be difficult to distinguish anaphylaxis from asthma , syncope , and panic attacks . | C2, C1 | C2 | B2 | A1 | Không có từ nào trong AWL dù thuật ngữ y khoa rất khó. AWL không đo loại khó này. |

## Phần 5. Ca cây AWL sai (phần của Ka)

| ID | Câu | Đích | Cây | Mật độ AWL | Giải thích (AI soạn) |
| --- | --- | --- | --- | ---: | --- |
| `score_dev_0009` | It 's 10 p. m. | A1 | C1 | 0,25 | **Lỗi có thật trong dữ liệu đặc trưng:** chữ `s` của `'s` bị tính là từ AWL. Xem phần 6. |
| `score_dev_0120` | The movie is Hitchcock 's . | A2 | C1 | 0,20 | Cùng lỗi `s`. |
| `score_dev_0408` | I feel it necessary to do exercises . | B1 | A1 | 0 | Không có từ AWL nên bị đoán A1. |
| `wiki_dev_0275` | The reason that Specialized was based on Special English is related to their respective usage . | B2 | A1 | 0 | "Không có từ AWL" không có nghĩa là câu dễ. |
| `wiki_dev_0476` | Originally , ventriloquism was a religious practice . | C1 | A1 | 0 | "ventriloquism" rất khó nhưng không thuộc AWL. |
| `wiki_dev_0636` | The posterior pituitary is actually an extension of the hypothalamus . | C2 | A1 | 0 | Thuật ngữ sinh học không phải từ học thuật chung. |

## Phần 6. Gom nhóm, kiểm tra giả thuyết trên dev

| Nhóm lỗi | Giả thuyết | Số liệu trên dev | Kết luận |
| --- | --- | --- | --- |
| Kéo về mức giữa | LR đoán cao câu dễ và đoán thấp câu khó, thay vì "cứ câu ngắn là đoán sai". | Câu ≤7 từ nhãn A1, A2: 69/125 đoán cao, 2/125 đoán thấp. Câu ≤7 từ nhãn từ B2 trở lên: 33/57 đoán thấp, 7/57 đoán cao. Câu >15 từ: 143/345 đoán thấp, 46/345 đoán cao. | Được ủng hộ trên dev. |
| Từ hiếm | Câu C1, C2 bị đoán thấp vì có nhiều từ mô hình chưa biết. | Tỉ lệ từ chưa biết: 17,9% ở 169 câu đoán thấp, 16,2% ở 91 câu đoán đúng. | Chênh lệch nhỏ, chưa đủ để khẳng định. |
| Nhãn không chắc | Mô hình khó hơn ở những câu chuyên gia bất đồng. | Accuracy 38,2% khi bất đồng (n=863), 45,1% khi đồng ý (n=503). Khi bất đồng, LR trùng ít nhất một trong hai nhãn ở 76,8% số câu. | Được ủng hộ. Một phần lỗi đến từ quy ước lấy max. |
| Không có từ AWL | Cây coi mọi câu không có từ AWL là A1. | 829 câu không có từ AWL đều bị đoán A1. Thật ra chỉ 38 câu là A1, còn 306 câu từ B2 trở lên. | Đã xác nhận. |
| Lỗi đặc trưng `s` | Khi trích PDF, phần cuối của "acknowledgement**s**" bị xuống dòng nên `s` thành một "từ AWL". | Chữ `s` khớp ở 73/1.366 câu dev và 425/7.177 câu train. Bỏ nó đi thì dự đoán của cây đổi ở 55 câu dev. | Đã xác nhận. Đây là giới hạn của kết quả AWL đã đóng băng. |

**Kết luận trong phạm vi bằng chứng:** LR dựa nhiều vào từ cụ thể và văn phong, chưa thấy được cấu trúc câu. Một phần lỗi đến từ nhãn không chắc. Đặc trưng AWL có một lỗi trích xuất, nên kết quả của cây chỉ đại diện cho **cách cài đặt này**.

**Bước tiếp theo khả thi:** sửa `s` trong danh sách AWL rồi so sánh lại trên dev, ghi thành một thí nghiệm mới, không sửa kết quả đã đóng băng.
