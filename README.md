# payment-anomaly-detector

## Ứng dụng mô hình học máy để phát hiện bất thường trong hệ thống thanh toán trực tuyến

---

## 1. Bối cảnh và Phạm vi bài toán (Đa kịch bản bất thường)

Thanh toán điện tử tại Việt Nam đang tăng trưởng nhanh trên nền hạ tầng chuyển mạch liên ngân hàng. Năm 2024, hệ thống NAPAS xử lý 9,56 tỷ giao dịch với tổng giá trị 61 triệu tỷ đồng; sang năm 2025, số lượng giao dịch tiếp tục tăng 23,7% và giá trị tăng 8,7% so với năm 2024, đạt bình quân hơn 32 triệu giao dịch mỗi ngày. Đi kèm với quy mô giao dịch trực tuyến tức thời là sự gia tăng của các rủi ro gian lận và lạm dụng hạ tầng thanh toán (riêng năm 2025, NAPAS đã gửi hơn 3,4 triệu lượt cảnh báo giao dịch đáng ngờ tới khách hàng và triển khai công cụ cảnh báo tới 47 ngân hàng).

Trong thực tế vận hành, hệ thống thanh toán trực tuyến không chỉ đối mặt với một hình thức vi phạm đơn lẻ mà phải xử lý **đa kịch bản bất thường (Multi-Scenario Anomalies)** kết hợp giữa **hành vi truy cập kỹ thuật (thiết bị, hệ điều hành, trình duyệt, địa chỉ IP/Proxy)** và **hành vi dòng tiền (số tiền, tần suất, cấu trúc tài khoản gửi/nhận)**:

```text
Kịch bản 1 - Chiếm đoạt tài khoản (Account Takeover - ATO):
  Kẻ gian đăng nhập từ thiết bị lạ và địa chỉ IP/Proxy mới rồi chuyển tiền
  giá trị lớn ngay lập tức với khoảng cách thao tác rất ngắn.

Kịch bản 2 - Dò mật khẩu & Lạm dụng truy cập tự động (Credential Stuffing / Bot):
  Sử dụng kịch bản tự động gọi liên tục vào hệ thống từ một hoặc nhiều IP/thiết bị
  để dò quét xác thực hoặc thu thập lịch sử giao dịch với nhịp độ máy móc.

Kịch bản 3 - Chia nhỏ giao dịch né ngưỡng (Structuring / Smurfing):
  Chia khoản tiền lớn thành nhiều giao dịch nhỏ nằm sát dưới ngưỡng cảnh báo
  nhằm vô hiệu hóa các bộ lọc giám sát theo mệnh giá.

Kịch bản 4 - Tài khoản chân rơm & Tiền vào ra ngay (Money Mule / Pass-Through):
  Tài khoản trung gian nhận tiền liên tục từ nhiều nguồn khác nhau rồi chuyển tiếp
  gần như tức thời để che giấu nguồn gốc dòng tiền.

Kịch bản 5 - Lợi dụng hạ tầng thanh toán cho cờ bạc trực tuyến:
  Nhà cái thu mua tài khoản "chân rơm" nhận hàng trăm khoản cược nhỏ (1k–10k)
  và dùng token tự động truy vấn lịch sử mã giao dịch để tính kết quả chẵn/lẻ.
```

---

## 2. Vấn đề của hệ thống giám sát truyền thống

Các hệ thống giám sát truyền thống dựa trên **quy tắc cứng (Rule-based)** không đáp ứng được bài toán trên vì bốn nguyên nhân:

- **Kẻ tấn công thay đổi phương thức liên tục để né ngưỡng:** Các biến thể chia nhỏ số tiền hoặc điều chỉnh nhịp truy vấn nằm ngay dưới ngưỡng tĩnh (`T1, T2, T3`) sẽ bị bỏ lọt hoàn toàn.
- **Giao dịch hợp lệ về mặt hình thức:** Phiên xác thực bị đánh cắp hoặc các khoản tiền chia nhỏ vẫn hợp lệ ở tầng bảo mật cơ bản nếu không xét chuỗi hành vi theo thời gian và độ ổn định thiết bị/IP.
- **Tỷ lệ cảnh báo nhầm rất cao (High False Positive Rate):** Khi hạ ngưỡng quy tắc cứng để tăng độ phủ, hệ thống chặn nhầm hàng loạt giao dịch hợp lệ của khách hàng thật (thực nghiệm cho thấy Rule-based có tỷ lệ cảnh báo nhầm lên tới 51,81%).
- **Phản ứng chậm trễ:** Quy tắc phải cập nhật thủ công nên thời điểm phát hiện thường quá muộn so với thời điểm hành vi bất thường bắt đầu.

---

## 3. Mục tiêu

Xây dựng hệ thống tự động phát hiện và phân loại bất thường trong thanh toán trực tuyến dựa trên **kiến trúc học máy hai tầng (Isolation Forest + LSTM/Boosting)** huấn luyện trên **dữ liệu giao dịch và định danh thiết bị thực tế (không giả lập)** — đồng thời trực quan hóa kết quả trên bảng điều khiển **React + D3.js** và đề xuất hướng xử lý tuân thủ theo Luật Phòng, chống rửa tiền năm 2022.

---

## 4. Dữ liệu thực nghiệm — Bộ dữ liệu thực tế IEEE-CIS Fraud Detection

Đề tài sử dụng **100% dữ liệu giao dịch trực tuyến thực tế** từ bộ dữ liệu chuẩn quốc tế **IEEE-CIS Fraud Detection** (do tập đoàn bảo mật thanh toán **Vesta Corporation** và **IEEE Computational Intelligence Society** công bố trên Kaggle), tuyệt đối không sử dụng dữ liệu giả lập tự sinh.

### Quy mô và Phân chia dữ liệu (Chống rò rỉ theo thời gian)

- **Tổng quy mô có nhãn:** **590.540 giao dịch trực tuyến thực tế** (trong đó có **20.663 giao dịch bất thường**, chiếm tỷ lệ **3,50%**) kết hợp cùng **144.233 bản ghi định danh thiết bị/mạng**, gồm **434 trường nguyên bản** nối qua khóa `TransactionID`.
- **Chiến lược chia dữ liệu (Temporal Split 70/30 theo `TransactionDT`):**
  - **Tập Huấn luyện (Train - 70% đầu):** `413.378` giao dịch (gồm `14.538` mẫu bất thường).
  - **Tập Kiểm thử (Test - 30% cuối):** `177.162` giao dịch (gồm `6.125` mẫu bất thường).

### Cấu trúc các nhóm trường dữ liệu chính

| Nhóm dữ liệu | Trường đại diện trong IEEE-CIS | Mô tả nghiệp vụ |
| :--- | :--- | :--- |
| **1. Định danh & Thời gian** | `TransactionID`, `TransactionDT`, `tx_hour` | Mã giao dịch duy nhất, dấu thời gian thực (giây) và khung giờ thực hiện giao dịch trong ngày |
| **2. Tài khoản & Giao dịch** | `TransactionAmt`, `ProductCD`, `card1`–`card6`, `addr1`–`addr2`, `P_emaildomain`, `R_emaildomain` | Số tiền giao dịch, loại dịch vụ thanh toán, thông tin thẻ/tài khoản, mã vùng địa lý và tên miền email người gửi/nhận |
| **3. Thiết bị & Mạng (Identity)** | `DeviceType`, `DeviceInfo`, `id_01`–`id_38` | Loại thiết bị (`mobile`/`desktop`), tên thiết bị/hệ điều hành, trình duyệt (`id_31`), điểm tín nhiệm thiết bị, điểm IP, Proxy ẩn danh và trạng thái phiên đăng nhập |
| **4. Mật độ & Khoảng cách (Vesta)** | `C1`–`C14`, `D1`–`D15`, `M1`–`M9`, `V1`–`V339` | Tần suất liên kết thực thể, khoảng cách thời gian giữa các giao dịch trước đó và các đặc trưng hành vi tổng hợp |
| **5. Đặc trưng cửa sổ trượt (`UID`)** | `UID`, `tx_time_diff`, `uid_tx_count`, `uid_unique_devices`, `amt_ratio_mean`, `uid_amt_std`, `amt_change_ratio` | Tái tạo định danh khách hàng (`UID = card1 + addr1`) để trích xuất khoảng cách giữa 2 yêu cầu liên tiếp, tổng tần suất giao dịch, số thiết bị khác nhau và tỷ lệ đột biến số tiền |

---

## 5. Kiến trúc hệ thống

### Luồng vận hành (MLOps)

```text
[Kaggle / Google Colab GPU]           [Lưu trữ Model]             [DigitalOcean Server]
            │                                │                              │
Add Input: IEEE-CIS Dataset                  │                        Load trọng số model
Nén RAM (~70%) & Trích xuất UID  ──────►  if_tier1.pkl     ──────►    FastAPI REST API
Huấn luyện Tầng 1 + Tầng 2                xgb_tier2.pkl                     │
Xuất bảng kết quả thực nghiệm             lstm_tier2.pt               React + D3.js
                                                                        Dashboard
```

> **Lưu ý:** Kafka và Filebeat xuất hiện trong sơ đồ kiến trúc tổng thể của luận văn để thể hiện khả năng mở rộng theo thời gian thực (streaming) — không dựng trực tiếp trong phạm vi triển khai thử nghiệm.

### Quy trình xử lý 2 tầng (Đối sánh với Rule-based và Mô hình 1 tầng)

```text
Dữ liệu Giao dịch & Định danh Thiết bị (IEEE-CIS)
        │
        ▼
Trích xuất đặc trưng theo định danh khách hàng (UID)
(tần suất giao dịch, khoảng cách yêu cầu, độ ổn định
 thiết bị/IP/Proxy, tỷ lệ biến động số tiền, chuỗi cửa sổ)
        │
        ▼
┌─────────────────────────────────────────┐
│  Tầng 1: Isolation Forest               │ ──── Rủi ro thấp ──► Bỏ qua mạng chuỗi LSTM
│  (Lọc nhanh & chấm điểm ngoại lai;      │                      (Tiết kiệm chi phí tính toán)
│   đối sánh trực tiếp với LOF)           │
└─────────────────────────────────────────┘
        │ Vượt ngưỡng nghi ngờ (High-Risk)
        ▼
┌─────────────────────────────────────────┐
│  Tầng 2: Phân loại chi tiết             │ ──── Kết hợp chuỗi cửa sổ LSTM (seq_len=3)
│  (LSTM + Softmax & Boosting kết hợp     │      + Điểm ngoại lai Tầng 1 (Carcillo et al.)
│   điểm ngoại lai Tầng 1)                │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Bảng điều khiển React + D3.js          │ ──── Trực quan hóa + Đề xuất xử lý tuân thủ STR
└─────────────────────────────────────────┘
```

### Chi tiết các nhóm phương pháp thực nghiệm

| Nhóm / Tầng | Mô hình | Vai trò trong thực nghiệm |
| :--- | :--- | :--- |
| **Baseline Quy tắc cứng** | **Rule-Based (`R1, R2, R3`)** | Đặt ngưỡng tĩnh trên khoảng cách yêu cầu & tần suất (`R1`), số lượng thiết bị trên cùng `UID` (`R2`) và đột biến số tiền (`R3`). |
| **Mô hình 1 tầng (Đơn giản)** | **Logistic Regression, Decision Tree** | Mô hình học máy cơ bản dùng làm mốc tham chiếu tốc độ và độ chính xác. |
| **Mô hình 1 tầng (Tổ hợp)** | **Random Forest, XGBoost** | Mô hình cây quyết định tổ hợp chạy độc lập trên toàn bộ tập dữ liệu bảng. |
| **Tầng 1 (Lọc nhanh)** | **Isolation Forest** *(đối sánh **LOF**)* | Đánh giá nhanh mức độ ngoại lai với độ phức tạp tuyến tính, sàng lọc các luồng nghi ngờ cần phân tích chuỗi chuyên sâu. |
| **Tầng 2 (Phân loại chuỗi)** | **LSTM + Softmax** *(cửa sổ `seq_len=3`)* | Học phụ thuộc chuỗi thời gian trên lịch sử giao dịch liên tiếp của từng `UID`, kết hợp cùng mô hình Boosting và điểm ngoại lai Tầng 1. |

---

## 6. Kết quả thực nghiệm trên dữ liệu thực tế IEEE-CIS

Kết quả đánh giá khách quan trên **177.162 giao dịch kiểm thử** (gồm **6.125 giao dịch bất thường thực tế**, ngưỡng phân loại tối ưu trên tập Validation = `0.46`):

| Mô hình / Cấu hình | Accuracy | Precision | Recall (Độ phủ) | F1-Score | AUC-ROC | FPR (Cảnh báo nhầm) | Thời gian (`ms/yêu cầu`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Rule-Based (Baseline)** | 0,4897 | 0,0467 | 0,7087 | 0,0876 | 0,5953 | 0,5181 | 0,0000 |
| **2. Isolation Forest (Tầng 1 độc lập)** | 0,9298 | 0,1327 | 0,1863 | 0,1550 | 0,7065 | 0,0436 | 0,0098 |
| **3. Local Outlier Factor (LOF)** | 0,9188 | 0,0680 | 0,1061 | 0,0829 | 0,5269 | 0,0521 | 0,1833 |
| **4. Logistic Regression** | 0,9378 | 0,1934 | 0,2519 | 0,2188 | 0,7809 | 0,0376 | 0,0001 |
| **5. Decision Tree** | 0,9714 | 0,7196 | 0,2833 | 0,4065 | 0,8001 | 0,0040 | 0,0002 |
| **6. Random Forest (1 tầng)** | 0,9731 | 0,8502 | 0,2705 | 0,4105 | 0,8900 | 0,0017 | 0,0065 |
| **7. XGBoost (1 tầng - Độc lập)** | 0,9750 | 0,7208 | 0,4501 | 0,5542 | 0,9217 | 0,0062 | 0,0074 |
| **8. LSTM Chuỗi cửa sổ (`seq_len=3`)** | 0,9596 | 0,4242 | 0,4736 | 0,4476 | 0,8657 | 0,0230 | 0,0032 |
| **9. Kiến trúc 2 Tầng (Đề xuất)** | **0,9727** | **0,6471** | **0,4651** | **0,5412** | **0,9168** | **0,0091** | **0,0049** |

### Nhận xét chính từ kết quả thực nghiệm:

- **So với Quy tắc cứng (Rule-Based):** Rule-based bị cảnh báo nhầm tới **51,81% (`FPR = 0,5181`)** khiến `F1-Score` chỉ đạt `0,0876`. Kiến trúc 2 tầng giảm tỷ lệ cảnh báo nhầm xuống chỉ còn **0,91%** (giảm **57 lần** cảnh báo giả) và nâng `F1-Score` gấp **6,2 lần** (`0,5412`), `AUC-ROC` đạt `0,9168`.
- **So sánh tại Tầng 1 (Isolation Forest vs LOF):** Isolation Forest đạt `AUC-ROC = 0,7065` (vượt xa `0,5269` của LOF) và thời gian xử lý nhanh gấp **18,7 lần** (`0,0098 ms` so với `0,1833 ms/yêu cầu`).
- **Vai trò của chuỗi thời gian LSTM và Kiến trúc 2 tầng:** Mô hình `LSTM Chuỗi cửa sổ (seq_len=3)` đạt độ phủ cao nhất trong các mô hình học máy (`Recall = 47,36%`) và vượt qua cả Random Forest (`F1 = 0,4476` so với `0,4105`). Nhờ cơ chế lọc phân tầng chỉ kích hoạt LSTM cho nhóm giao dịch rủi ro cao từ Tầng 1, **Kiến trúc 2 tầng** đạt **độ phủ (`Recall = 46,51%`) cao hơn cả XGBoost 1 tầng (`45,01%`) lẫn Random Forest (`27,05%`)**, đồng thời **rút ngắn 33,8% thời gian xử lý** so với chạy XGBoost 1 tầng (`0,0049 ms` so với `0,0074 ms/yêu cầu`).

---

## 7. Hướng xử lý sau phát hiện

| Mức độ & Nhóm dấu hiệu bất thường | Hành động đề xuất | Giải thích nghiệp vụ & Tuân thủ |
| :--- | :--- | :--- |
| **Mức Trung bình — Bất thường tần suất ngắn hạn** | Giới hạn tốc độ yêu cầu (Rate Limiting) + Yêu cầu xác thực bổ sung (OTP) | Làm chậm kịch bản truy vấn tự động, tránh chặn nhầm khách hàng thật đang giao dịch. |
| **Mức Cao — Bất thường Thiết bị & IP/Proxy (ATO)** | Vô hiệu hóa phiên xác thực + Tạm giữ giao dịch + Cảnh báo nhóm Bảo mật | Ngăn chặn kịp thời hành vi chiếm đoạt tài khoản chuyển tiền từ thiết bị lạ. |
| **Mức Cao — Bất thường cấu trúc dòng tiền (Mule / Smurfing)** | Tạm khóa chiều ghi nợ + Chuyển hồ sơ cho nhóm Tuân thủ (Compliance) | Rà soát và lập Báo cáo giao dịch đáng ngờ (STR) gửi Ngân hàng Nhà nước theo Luật Phòng, chống rửa tiền số 14/2022/QH15. |
| **Mức Nghiêm trọng — Đa dấu hiệu kết hợp** | Vô hiệu hóa phiên + Đóng băng tài khoản tạm thời + Báo cáo khẩn liên bộ phận | Xử lý khẩn cấp các vụ việc kết hợp cả xâm nhập trái phép và luân chuyển dòng tiền bất hợp pháp. |

---

## 8. Cấu trúc thư mục

```text
payment-anomaly-detector/
│
├── data/                               # Dữ liệu IEEE-CIS Fraud Detection
│   ├── raw/                            # train_transaction.csv, train_identity.csv (.gitignore)
│   └── processed/                      # Dữ liệu đã tối ưu bộ nhớ & trích xuất chuỗi UID (.gitignore)
│
├── notebooks/                          # Kaggle / Google Colab Notebooks
│   ├── 01_eda_and_memory_opt.ipynb     # Khám phá dữ liệu & tối ưu hóa RAM (~70%)
│   ├── 02_feature_engineering.ipynb    # Tái tạo UID & trích xuất đặc trưng cửa sổ thời gian
│   ├── 03_train_tier1_if_vs_lof.ipynb  # Huấn luyện và đối sánh Tầng 1 (Isolation Forest vs LOF)
│   └── 04_train_tier2_cascade.ipynb    # Huấn luyện LSTM, XGBoost, RF & Đánh giá Kiến trúc 2 tầng
│
├── ml/                                 # Học máy & Kết quả thực nghiệm
│   ├── features.py                     # Pipeline trích xuất đặc trưng UID & chuỗi thời gian
│   ├── isolation_forest.py             # Bộ lọc nhanh Tầng 1
│   ├── lstm_model.py                   # Mô hình chuỗi PyTorch LSTM Tầng 2
│   └── saved_models/                   # Trọng số mô hình xuất từ Kaggle (.gitignore)
│       ├── if_tier1.pkl
│       ├── xgb_tier2.pkl
│       ├── lstm_tier2.pt
│       └── experiment_results_final.csv
│
├── backend/                            # FastAPI Backend
│   ├── main.py                         # Điểm khởi chạy dịch vụ REST API
│   ├── routers/
│   │   ├── predict.py                  # API dự đoán 2 tầng & đo thời gian suy luận
│   │   └── logs.py                     # API truy vấn lịch sử giao dịch & cảnh báo
│   ├── services/
│   │   └── model_service.py            # Nạp và vận hành pipeline suy luận 2 tầng
│   └── requirements.txt
│
├── frontend/                           # React + D3.js Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx           # Trang giám sát chính
│   │   │   ├── AnomalyChart.jsx        # Biểu đồ trực quan hóa D3.js
│   │   │   ├── LogTable.jsx            # Bảng tra cứu giao dịch & thiết bị
│   │   │   └── AlertPanel.jsx          # Bảng chi tiết cảnh báo & gợi ý xử lý STR
│   │   └── App.jsx
│   └── package.json
│
├── docs/                               # Tài liệu nghiên cứu
│   ├── architecture.png                # Sơ đồ kiến trúc hệ thống
│   └── thesis/                         # Đề cương & Bản thảo luận văn
│
├── docker-compose.yml                  # Đóng gói toàn hệ thống
├── .gitignore
└── README.md
```

---

## 9. Công nghệ sử dụng

| Tầng | Công nghệ |
| :--- | :--- |
| **Dữ liệu thực nghiệm** | Bộ dữ liệu thực tế **IEEE-CIS Fraud Detection** (`590.540` giao dịch, `434` trường) |
| **Môi trường huấn luyện** | Kaggle Notebooks / Google Colab (GPU) |
| **Tiền xử lý & Đặc trưng** | Python, Pandas, NumPy, Scikit-learn (`RobustScaler`, `SimpleImputer`) |
| **Mô hình Tầng 1 (Lọc nhanh)** | Scikit-learn (`Isolation Forest`, đối sánh `Local Outlier Factor - LOF`) |
| **Mô hình Tầng 2 & Đối sánh** | PyTorch (`LSTM + Softmax`), `XGBoost`, `Random Forest`, `Decision Tree`, `Logistic Regression` |
| **API Backend** | FastAPI |
| **Giao diện trực quan hóa** | React + D3.js |
| **Đóng gói & Triển khai** | Docker Compose + DigitalOcean |

---

## 10. Đóng góp chính

1. **Thực nghiệm trên dữ liệu giao dịch và định danh thiết bị thực tế quy mô lớn:** Khai thác kết hợp 394 trường giao dịch và 41 trường thiết bị/IP của bộ dữ liệu **IEEE-CIS (590.540 bản ghi)**, tái tạo định danh `UID` và trích xuất đặc trưng cửa sổ thời gian để phát hiện đa kịch bản bất thường mà không dùng dữ liệu giả lập.
2. **Thiết kế kiến trúc xử lý 2 tầng hiệu quả:** Kết hợp điểm ngoại lai từ **Isolation Forest (Tầng 1)** với mô hình chuỗi **LSTM (`seq_len=3`)** và **Boosting (Tầng 2)**, giúp đạt `AUC-ROC = 0,9168`, nâng độ phủ (`Recall = 46,51%`) cao hơn mô hình đơn tầng và giảm **33,8%** thời gian suy luận so với chạy XGBoost độc lập trên toàn bộ lưu lượng.
3. **So sánh thực nghiệm có hệ thống ở 3 cấp:** Đối chiếu định lượng giữa **Rule-based baseline**, các mô hình đơn giản (**Logistic Regression, Decision Tree**), các mô hình tổ hợp (**Random Forest, XGBoost, LOF**) và **Kiến trúc 2 tầng** về cả hiệu năng phát hiện lẫn tốc độ xử lý (`ms/yêu cầu`).
4. **Hỗ trợ ra quyết định và tuân thủ pháp lý:** Xây dựng bảng điều khiển **React + D3.js** kết nối **FastAPI** đóng gói bằng **Docker**, giải thích nguyên nhân cảnh báo và đề xuất hướng xử lý gắn với quy định báo cáo giao dịch đáng ngờ (STR) theo Luật Phòng, chống rửa tiền 2022.

---

## 11. Kế hoạch thực hiện (6 tháng: 10/2026 – 03/2027)

| Tháng | Nội dung công việc |
| :---: | :--- |
| **1 (10/2026)** | Nghiên cứu cơ sở lý thuyết, khảo sát công trình trong/ngoài nước, phân tích đa kịch bản bất thường và Luật Phòng, chống rửa tiền 2022 |
| **2 (11/2026)** | Thu thập, tối ưu hóa bộ nhớ, tái tạo định danh `UID` và trích xuất đặc trưng cửa sổ thời gian trên bộ dữ liệu thực tế IEEE-CIS |
| **3 (12/2026)** | Huấn luyện và tinh chỉnh kiến trúc 2 tầng (Isolation Forest, LSTM) cùng các mô hình đối sánh trên Kaggle/Colab GPU |
| **4 (01/2027)** | Xây dựng dịch vụ FastAPI, bảng điều khiển React + D3.js và đóng gói Docker Compose trên DigitalOcean |
| **5 (02/2027)** | Tổng hợp kết quả đánh giá 3 cấp, phân tích hiệu năng/thời gian xử lý và viết bản thảo các chương luận văn |
| **6 (03/2027)** | Hoàn thiện cuốn luận văn, kiểm thử hệ thống demo và bảo vệ trước Hội đồng |

---

*Học viên thực hiện: Nguyễn Huỳnh Thanh Triết (MSHV: 8480101250013)*  
*Giảng viên hướng dẫn: TS. Huỳnh Đệ Thủ — TS. Phạm Công Thành*  
*Chương trình: Thạc sĩ Khoa học Máy tính (Khóa 2025–2027) — Trường Đại học Quốc tế Sài Gòn (SIU)*
