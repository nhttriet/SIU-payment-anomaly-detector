# payment-anomaly-detector

## Ứng dụng mô hình học máy để phát hiện bất thường trong hệ thống thanh toán trực tuyến

---

## 1. Bối cảnh và Phạm vi bài toán (Đa kịch bản bất thường)

Thanh toán điện tử tại Việt Nam đang tăng trưởng mạnh mẽ trên nền hạ tầng chuyển mạch liên ngân hàng NAPAS với hơn 9,56 tỷ giao dịch (61 triệu tỷ đồng) năm 2024 và tiếp tục tăng 23,7% về số lượng giao dịch vào năm 2025 (bình quân hơn 32 triệu giao dịch mỗi ngày). Đi kèm với quy mô giao dịch trực tuyến tức thời là sự gia tăng phức tạp của các hành vi gian lận, xâm nhập trái phép và lợi dụng hạ tầng thanh toán. Riêng trong năm 2025, hệ thống đã phát đi hơn 3,4 triệu lượt cảnh báo giao dịch đáng ngờ tới khách hàng qua 47 ngân hàng.

Thay vì chỉ giới hạn ở một hình thức vi phạm đơn lẻ, hệ thống thanh toán trực tuyến trong thực tế phải đối mặt đồng thời với nhiều kịch bản bất thường (Multi-Scenario Anomalies) kết hợp giữa **tầng truy cập kỹ thuật (thiết bị, địa chỉ IP, phiên xác thực)** và **tầng dòng tiền nghiệp vụ (số tiền, tần suất, mạng lưới tài khoản gửi/nhận)**:

1. **Chiếm đoạt tài khoản (Account Takeover - ATO):** Kẻ gian đánh cắp thông tin xác thực hoặc phiên đăng nhập (token/session), truy cập từ thiết bị lạ và địa chỉ IP/Proxy bất thường, sau đó thực hiện giao dịch rút/chuyển khoản giá trị lớn ngay lập tức.
2. **Dò mật khẩu và Lạm dụng truy cập tự động (Credential Stuffing & API/Session Abuse):** Sử dụng kịch bản tự động (bot) gọi liên tục vào hệ thống từ các dải IP xoay vòng để dò quét tài khoản hoặc liên tục truy vấn lịch sử giao dịch với nhịp độ máy móc.
3. **Chia nhỏ giao dịch né ngưỡng giám sát (Structuring / Smurfing):** Chia một khoản tiền bất hợp pháp lớn thành nhiều giao dịch nhỏ nằm ngay sát dưới ngưỡng cảnh báo tự động nhằm vô hiệu hóa các bộ lọc theo mệnh giá.
4. **Tài khoản chân rơm và Luân chuyển tiền nhanh (Money Mule & Pass-Through):** Sử dụng các tài khoản cá nhân thu mua/thuê mượn làm cổng trung gian nhận hàng trăm khoản tiền nhỏ liên tục từ nhiều nguồn khác nhau rồi chuyển tiếp ngay để che giấu nguồn gốc dòng tiền.
5. **Lợi dụng hạ tầng thanh toán cho cờ bạc trực tuyến:** Kết hợp tài khoản chân rơm nhận tiền đặt cược nhỏ (1.000đ – 10.000đ) và đánh cắp token để đọc lịch sử mã giao dịch tự động nhằm phân định thắng thua ngoài hệ thống ngân hàng.

---

## 2. Vấn đề của hệ thống giám sát truyền thống

Các hệ thống giám sát dựa trên **quy tắc cứng (Rule-based)** truyền thống bộc lộ bốn hạn chế lớn trước các kịch bản trên:

- **Dễ bị lách ngưỡng (Threshold Evasion):** Kẻ tấn công liên tục điều chỉnh hành vi (chia nhỏ số tiền sát dưới ngưỡng, giãn nhịp truy vấn, xoay vòng tài khoản nhận) để nằm dưới ngưỡng kích hoạt tĩnh.
- **Điểm mù trước giao dịch hợp lệ về hình thức:** Các giao dịch chia nhỏ hoặc sử dụng phiên xác thực hợp lệ đã bị đánh cắp không bị chặn ở tầng bảo mật cơ bản nếu không phân tích chuỗi hành vi theo thời gian và độ ổn định của thiết bị/IP.
- **Tỷ lệ cảnh báo nhầm cao (High False Positive Rate):** Việc hạ thấp ngưỡng quy tắc cứng để bắt gian lận khiến số lượng cảnh báo giả tăng vọt, gây quá tải cho bộ phận vận hành và làm gián đoạn trải nghiệm của người dùng thật.
- **Độ trễ cập nhật lớn:** Quy tắc phải được viết và tinh chỉnh thủ công sau khi thiệt hại đã xảy ra, không kịp thích ứng với các biến thể tấn công mới.

---

## 3. Mục tiêu nghiên cứu

Xây dựng hệ thống phát hiện bất thường trong thanh toán trực tuyến dựa trên **kiến trúc học máy hai tầng (Two-Stage Architecture)** trên **dữ liệu giao dịch và định danh thiết bị thực tế**:

- Kết hợp **Tầng 1 (Isolation Forest — lọc nhanh không giám sát)** và **Tầng 2 (LSTM / Mô hình có giám sát — phân loại chi tiết)** để cân bằng giữa **độ phủ phát hiện (Recall)**, **độ chính xác (Precision)** và **chi phí thời gian xử lý (ms/yêu cầu)**.
- **So sánh thực nghiệm toàn diện ở 3 cấp (Tầng 1, Tầng 2, Đầu cuối)** giữa kiến trúc đề xuất với **Baseline dựa trên quy tắc cứng (Rule-based)**, các **mô hình một tầng đơn giản (Logistic Regression, Decision Tree)** và các **mô hình đối sánh (LOF, Random Forest, XGBoost)** cả về hiệu năng phát hiện lẫn tốc độ suy luận.
- Trực quan hóa kết quả và nguyên nhân chi tiết trên **bảng điều khiển React + D3.js**, đồng thời đề xuất hướng xử lý phân tầng hỗ trợ bộ phận bảo mật và tuân thủ lập báo cáo giao dịch đáng ngờ (STR) theo Luật Phòng, chống rửa tiền số 14/2022/QH15.

---

## 4. Dữ liệu thực nghiệm — Bộ dữ liệu thực tế IEEE-CIS Fraud Detection

Đề tài sử dụng **100% dữ liệu giao dịch thanh toán trực tuyến thực tế** từ bộ dữ liệu chuẩn quốc tế **IEEE-CIS Fraud Detection** (do tập đoàn bảo mật thanh toán **Vesta Corporation** và **Hội Trí tuệ Tính toán IEEE** công bố trên Kaggle), hoàn toàn không sử dụng dữ liệu giả lập.

### Quy mô và Cấu trúc dữ liệu

Tập huấn luyện và kiểm định có nhãn gồm **590.540 giao dịch trực tuyến thực tế** (trong đó có **20.663 giao dịch bất thường/gian lận**, chiếm tỷ lệ **3,50%**) kết hợp cùng **144.233 bản ghi định danh kỹ thuật**, được liên kết qua khóa `TransactionID` trên 2 bảng dữ liệu (tổng cộng **434 trường nguyên bản**):

| Bảng dữ liệu | Số trường | Các nhóm thuộc tính thực tế chính |
| :--- | :--- | :--- |
| **1. Bảng Giao dịch (`train_transaction.csv`)** | 394 trường | - `TransactionID`: Mã định danh giao dịch<br>- `isFraud`: Nhãn mục tiêu (`0`: Bình thường, `1`: Bất thường/Gian lận)<br>- `TransactionDT`: Dấu thời gian thực tế của giao dịch (giây)<br>- `TransactionAmt`: Số tiền giao dịch thanh toán<br>- `ProductCD`: Mã loại sản phẩm/dịch vụ thanh toán<br>- `card1` – `card6`: Thông tin định danh thẻ/tài khoản, loại thẻ, ngân hàng phát hành<br>- `addr1`, `addr2`, `dist1`, `dist2`: Mã vùng địa lý và khoảng cách<br>- `P_emaildomain`, `R_emaildomain`: Tên miền email của người thanh toán và người nhận<br>- `C1` – `C14`: Các biến đếm tần suất liên kết thực thể (số lượng thẻ/địa chỉ/email gắn liền)<br>- `D1` – `D15`: Khoảng cách thời gian (timedelta) giữa các giao dịch trước đó<br>- `M1` – `M9` & `V1` – `V339`: Các biến đối khớp định danh và đặc trưng hành vi của Vesta |
| **2. Bảng Định danh & Thiết bị (`train_identity.csv`)** | 41 trường | - `DeviceType`: Loại thiết bị truy cập (`mobile` / `desktop`)<br>- `DeviceInfo`: Thông tin chi tiết phần cứng thiết bị, hệ điều hành, bản dựng<br>- `id_01` – `id_11`: Đặc trưng số đánh giá độ tin cậy thiết bị (device rating), điểm tên miền IP (IP domain rating), mức độ sử dụng Proxy ẩn danh, số lần đăng nhập thành công/thất bại và thời gian duy trì phiên trên trang<br>- `id_12` – `id_38`: Đặc trưng phân loại mạng, trình duyệt (`id_31`), hệ điều hành (`id_30`), trạng thái khớp IP/Proxy |

### Nhóm đặc trưng hành vi trích xuất phục vụ huấn luyện (Feature Engineering)

Từ dữ liệu gốc, hệ thống xây dựng định danh khách hàng (`UID` kết hợp từ thông tin tài khoản/thẻ `card1` và vùng địa lý `addr1`) và sắp xếp theo trình tự thời gian `TransactionDT` để trích xuất 4 nhóm đặc trưng cốt lõi:

| Nhóm đặc trưng | Biến đại diện | Hành vi Bình thường (`Nhãn 0`) | Hành vi Bất thường (`Nhãn 1`) |
| :--- | :--- | :--- | :--- |
| **1. Tần suất & Mật độ giao dịch** | `uid_tx_count`, `C1`–`C14` | Tần suất giao dịch tự nhiên, phân bố rải rác theo nhu cầu chi tiêu | Tăng đột biến trong cửa sổ thời gian ngắn hoặc lặp lại liên tục bất thường |
| **2. Khoảng cách thời gian (Velocity)** | `tx_time_diff`, `D1`–`D15`, `tx_hour` | Khoảng nghỉ tự nhiên giữa các thao tác; tập trung vào giờ sinh hoạt | Khoảng cách giữa các yêu cầu cực ngắn (vài giây) hoặc phát sinh dồn dập vào giờ khuya |
| **3. Độ ổn định Thiết bị & Địa chỉ IP** | `DeviceType`, `DeviceInfo`, `uid_unique_devices`, `id_01`–`id_38` | Thiết bị và địa chỉ IP ổn định, điểm rủi ro Proxy thấp | Thay đổi nhiều thiết bị/trình duyệt trên cùng một định danh `UID`, sử dụng Proxy/IP lạ |
| **4. Mẫu hình Số tiền giao dịch** | `TransactionAmt`, `amt_ratio_to_uid_mean`, `amt_decimal` | Giá trị phù hợp với lịch sử chi tiêu cá nhân | Đột biến gấp nhiều lần trung bình lịch sử (ATO) hoặc chia nhỏ lặp lại cùng mệnh giá (Smurfing) |

---

## 5. Kiến trúc hệ thống và Phương pháp so sánh

### Luồng vận hành (MLOps)

```text
[Kaggle: IEEE-CIS]          [Google Colab (GPU)]            [DigitalOcean Server]
        │                            │                                │
Tải dữ liệu thực tế         Nén tối ưu RAM (~70%)            Load trọng số mô hình
(Transaction + Identity) ─► Trích xuất đặc trưng UID/Chuỗi ─► FastAPI REST API
        │                   Huấn luyện & Đối sánh 3 nhóm              │
Lưu trữ bản raw             Lưu model vào Google Drive       React + D3.js Dashboard
                                                             (Đóng gói Docker Compose)
```

> **Lưu ý:** Kafka và Filebeat được thể hiện trong sơ đồ kiến trúc tổng thể của luận văn để minh họa khả năng mở rộng luồng dữ liệu thời gian thực (streaming) — không dựng trực tiếp trong phạm vi triển khai thử nghiệm.

### Quy trình xử lý 2 tầng và Thiết kế đối sánh 3 nhóm phương pháp

```text
Dữ liệu Giao dịch & Định danh Thiết bị (IEEE-CIS)
                        │
                        ▼
        Tiền xử lý & Trích xuất đặc trưng
   (Tần suất UID, Khoảng cách yêu cầu, Độ ổn định
     Thiết bị/IP/Proxy, Tỷ lệ biến động số tiền)
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────────┐ ┌───────────┐ ┌─────────────────────────┐
│ NHÓM A        │ │ NHÓM B    │ │ NHÓM C (ĐỀ XUẤT)        │
│ Rule-Based    │ │ Mô hình   │ │ Kiến trúc 2 Tầng        │
│ Baseline      │ │ 1 Tầng    │ │                         │
│               │ │           │ │ ┌─────────────────────┐ │
│ Quy tắc cứng  │ │ - LogReg  │ │ │ Tầng 1:             │ │
│ theo ngưỡng   │ │ - DecTree │ │ │ Isolation Forest    │─┼─► Bình thường (Bỏ qua)
│ tĩnh T1,T2,T3 │ │ - RF      │ │ │ (Lọc nhanh; đ/s LOF)│ │
└───────┬───────┘ │ - XGBoost │ │ └──────────┬──────────┘ │
        │         └─────┬─────┘ │            │ Nghi ngờ   │
        │               │       │            ▼            │
        │               │       │ ┌─────────────────────┐ │
        │               │       │ │ Tầng 2:             │ │
        │               │       │ │ LSTM / Boosting     │ │
        │               │       │ │ (Phân loại chi tiết)│ │
        │               │       │ └──────────┬──────────┘ │
        └───────────────┴───────┴────────────┼────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │ Đánh giá Hiệu năng & Tốc độ   │
                             │ + Bảng điều khiển React/D3.js │
                             └───────────────────────────────┘
```

### Chi tiết các mô hình thực nghiệm và đối sánh

| Nhóm phương pháp | Mô hình / Thành phần | Vai trò trong thực nghiệm |
| :--- | :--- | :--- |
| **Nhóm A: Baseline Quy tắc cứng** | **Rule-Based (`R1, R2, R3`)** | Thiết lập đường cơ sở theo ngưỡng tĩnh về tần suất giao dịch ngắn hạn (T1), số thiết bị/IP bất thường (T2) và tỷ lệ đột biến số tiền (T3) để đo mức suy giảm hiệu năng và thời gian xử lý. |
| **Nhóm B: Mô hình 1 tầng** | **Logistic Regression, Decision Tree** | Nhóm mô hình học máy đơn giản một tầng dùng làm mốc tham chiếu tốc độ suy luận và độ chính xác cơ bản. |
| **Nhóm B: Mô hình 1 tầng (Tổ hợp)** | **Random Forest, XGBoost** | Nhóm mô hình cây quyết định tổ hợp mạnh trên dữ liệu bảng khi chạy trực tiếp trên toàn bộ tập dữ liệu (không qua bộ lọc Tầng 1). |
| **Nhóm C: Kiến trúc 2 tầng (Tầng 1)** | **Isolation Forest** *(đối sánh với **LOF**)* | Lọc nhanh không giám sát với chi phí tính toán thấp, loại bỏ phần lớn giao dịch bình thường và chỉ giữ lại luồng nghi ngờ có điểm bất thường cao (ưu tiên tối đa hóa Độ phủ - Recall). |
| **Nhóm C: Kiến trúc 2 tầng (Tầng 2)** | **LSTM + Softmax** *(đối sánh với **RF, XGBoost**)* | Phân loại chi tiết các trường hợp nghi ngờ từ Tầng 1 dựa trên chuỗi hành vi theo thời gian của thực thể `UID` nhằm giảm thiểu tỷ lệ cảnh báo nhầm (False Positive Rate). |

---

## 6. Hướng xử lý sau phát hiện (Hỗ trợ ra quyết định & Tuân thủ)

Hệ thống phân tầng mức độ rủi ro từ điểm xác suất dự đoán của mô hình kết hợp với nhóm dấu hiệu vi phạm để đề xuất hành động cho bộ phận vận hành, bảo mật và tuân thủ:

| Mức độ cảnh báo & Loại bất thường | Hành động đề xuất trên hệ thống | Giải thích nghiệp vụ & Pháp lý |
| :--- | :--- | :--- |
| **Mức Trung bình — Bất thường tần suất truy cập / API** | Giới hạn tốc độ yêu cầu (Rate Limiting) + Yêu cầu xác thực bổ sung (Step-up Auth / OTP) | Làm chậm các kịch bản tự động (bot), tránh khóa nhầm khách hàng thật đang thao tác nhanh. |
| **Mức Cao — Bất thường Thiết bị / IP lạ (Nghi ngờ ATO)** | Vô hiệu hóa phiên/token hiện tại + Tạm giữ giao dịch chờ xác minh + Cảnh báo nhóm Bảo mật | Ngăn chặn tức thời hành vi chiếm đoạt tài khoản chuyển tiền ra ngoài qua thiết bị và Proxy lạ. |
| **Mức Cao — Bất thường cấu trúc dòng tiền (Smurfing / Mule)** | Tạm khóa chiều ghi nợ/chuyển đi + Chuyển hồ sơ cho bộ phận Tuân thủ (Compliance) | Phục vụ rà soát và lập Báo cáo giao dịch đáng ngờ (STR) gửi Ngân hàng Nhà nước theo Luật Phòng, chống rửa tiền số 14/2022/QH15. |
| **Mức Nghiêm trọng (Critical) — Đa dấu hiệu kết hợp** | Vô hiệu hóa phiên + Đóng băng tài khoản tạm thời + Báo cáo khẩn liên bộ phận (Bảo mật & Tuân thủ) | Xử lý các vụ tấn công có tổ chức kết hợp cả xâm nhập trái phép lẫn luân chuyển/rửa tiền quy mô lớn. |

---

## 7. Cấu trúc thư mục dự án

```text
payment-anomaly-detector/
│
├── data/                               # Dữ liệu thực nghiệm (IEEE-CIS Fraud Detection)
│   ├── raw/                            # train_transaction.csv, train_identity.csv (.gitignore)
│   └── processed/                      # Dữ liệu đã nén RAM, ghép bảng & tạo chuỗi UID (.gitignore)
│
├── notebooks/                          # Google Colab Notebooks
│   ├── 01_eda_and_memory_opt.ipynb     # Khám phá dữ liệu thực tế & tối ưu bộ nhớ (giảm ~70% RAM)
│   ├── 02_feature_engineering.ipynb    # Tạo định danh UID, đặc trưng cửa sổ thời gian & thiết bị
│   ├── 03_tier1_unsupervised.ipynb     # Huấn luyện & đối sánh Tầng 1 (Isolation Forest vs LOF)
│   ├── 04_tier2_and_baselines.ipynb    # Huấn luyện Tầng 2 (LSTM, RF, XGBoost) & Baseline (Rule, LR, DT)
│   └── 05_end_to_end_evaluation.ipynb  # Đánh giá tổng thể 3 cấp (Hiệu năng & Thời gian xử lý)
│
├── ml/                                 # Mô-đun Học máy
│   ├── features.py                     # Pipeline tiền xử lý và trích xuất đặc trưng
│   ├── rule_baseline.py                # Bộ quy tắc cứng R1-R3 theo ngưỡng tĩnh
│   ├── tier1_filter.py                 # Mô hình lọc nhanh Tầng 1 (Isolation Forest / LOF)
│   ├── tier2_classifier.py             # Mô hình phân loại Tầng 2 (LSTM / XGBoost / RF)
│   └── saved_models/                   # Trọng số mô hình đã huấn luyện (.gitignore)
│
├── backend/                            # Hệ thống API Backend (FastAPI)
│   ├── main.py                         # Điểm khởi chạy dịch vụ FastAPI
│   ├── routers/
│   │   ├── predict.py                  # Endpoint suy luận 2 tầng & đo độ trễ (ms)
│   │   └── alerts.py                   # Endpoint truy vấn sự kiện bất thường & gợi ý xử lý
│   ├── services/
│   │   └── inference_service.py        # Quản lý pipeline suy luận Tầng 1 -> Tầng 2
│   └── requirements.txt
│
├── frontend/                           # Bảng điều khiển trực quan hóa (React + D3.js)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx           # Giao diện giám sát tổng quan
│   │   │   ├── AnomalyChart.jsx        # Biểu đồ phân phối điểm bất thường & độ trễ D3.js
│   │   │   ├── TransactionTable.jsx    # Bảng tra cứu chi tiết giao dịch & thiết bị
│   │   │   └── AlertActionPanel.jsx    # Bảng giải thích nguyên nhân & đề xuất xử lý STR
│   │   └── App.jsx
│   └── package.json
│
├── docs/                               # Tài liệu nghiên cứu & Luận văn
│   ├── architecture.png                # Sơ đồ kiến trúc 2 tầng
│   └── thesis/                         # Đề cương, bản thảo luận văn & tổng hợp tài liệu
│
├── docker-compose.yml                  # Đóng gói toàn bộ hệ thống (Backend + Frontend)
├── .gitignore
└── README.md
```

---

## 8. Công nghệ sử dụng

| Hạng mục | Công nghệ / Thư viện |
| :--- | :--- |
| **Nguồn dữ liệu huấn luyện** | Bộ dữ liệu thực tế **IEEE-CIS Fraud Detection** (590.540 giao dịch + 144.233 bản ghi thiết bị/IP) |
| **Tiền xử lý & Đặc trưng** | Python, Pandas, NumPy, Scikit-learn, Imbalanced-learn (SMOTE / Class Weight) |
| **Môi trường huấn luyện** | Google Colab (GPU) kết hợp lưu trữ trọng số trên Google Drive |
| **Mô hình Tầng 1 (Lọc nhanh)** | Isolation Forest *(đối sánh với Local Outlier Factor - LOF)* |
| **Mô hình Tầng 2 (Phân loại)** | PyTorch (LSTM + Softmax), XGBoost, Random Forest |
| **Mô hình Baseline đối sánh** | Rule-Based (Quy tắc cứng T1, T2, T3), Logistic Regression, Decision Tree |
| **API Backend** | FastAPI, Uvicorn, Pydantic |
| **Giao diện trực quan hóa** | React, D3.js, Tailwind CSS |
| **Đóng gói & Triển khai** | Docker, Docker Compose, DigitalOcean |

---

## 9. Các chỉ số đánh giá thực nghiệm (Ba cấp: Tầng 1, Tầng 2, Đầu cuối)

1. **Nhóm chỉ số hiệu năng phát hiện:**
   - Độ phủ (Recall — chỉ số trọng tâm ở Tầng 1 để không bỏ lọt bất thường)
   - Độ chính xác (Precision) và Điểm trung hòa F1-score
   - Diện tích dưới đường cong ROC (AUC-ROC)
   - Tỷ lệ cảnh báo nhầm (False Positive Rate - FPR)
2. **Nhóm chỉ số hiệu năng vận hành & thời gian:**
   - Thời gian xử lý trung bình trên mỗi yêu cầu (`ms/yêu cầu`)
   - Thông lượng xử lý của hệ thống (`yêu cầu/giây`)
   - Độ trễ phát hiện tính từ thời điểm hành vi bất thường bắt đầu xuất hiện

---

## 10. Đóng góp chính của đề tài

1. **Khai thác kết hợp dữ liệu giao dịch và định danh thiết bị/mạng thực tế:** Xử lý và trích xuất đặc trưng hành vi theo định danh khách hàng (`UID`) và cửa sổ thời gian trên bộ dữ liệu thực tế quy mô lớn IEEE-CIS (590.540 bản ghi), nhận diện đa kịch bản bất thường mà không phụ thuộc vào dữ liệu giả lập.
2. **Thiết kế kiến trúc xử lý 2 tầng tối ưu chi phí tính toán:** Kết hợp bộ lọc nhanh không giám sát (Isolation Forest) ở Tầng 1 với mô hình phân loại chuyên sâu (LSTM / Boosting) ở Tầng 2, giúp giảm tải số lượng yêu cầu phải xử lý phức tạp mà vẫn duy trì độ chính xác cao và giảm cảnh báo nhầm.
3. **Đối sánh thực nghiệm có hệ thống:** So sánh định lượng trực tiếp giữa Quy tắc cứng (Rule-based), mô hình 1 tầng đơn giản (Logistic Regression, Decision Tree), mô hình tổ hợp (Random Forest, XGBoost) và kiến trúc 2 tầng trên cả hai khía cạnh: chất lượng phát hiện và thời gian suy luận.
4. **Xây dựng công cụ trực quan hóa và hỗ trợ tuân thủ pháp lý:** Tích hợp FastAPI, React và D3.js đóng gói qua Docker, cung cấp giao diện tra cứu nguyên nhân chi tiết từng cảnh báo và đề xuất hành động xử lý gắn với quy định báo cáo giao dịch đáng ngờ (STR) của Luật Phòng, chống rửa tiền 2022.

---

## 11. Kế hoạch thực hiện (6 tháng: 10/2026 – 03/2027)

| Tháng | Nội dung công việc trọng tâm |
| :---: | :--- |
| **Tháng 1 (10/2026)** | Nghiên cứu cơ sở lý thuyết, khảo sát tài liệu trong/ngoài nước, phân tích đa kịch bản bất thường và khung pháp lý Luật Phòng, chống rửa tiền 2022. |
| **Tháng 2 (11/2026)** | Thu thập, làm sạch, tối ưu hóa bộ nhớ và trích xuất đặc trưng cửa sổ thời gian/định danh `UID` trên bộ dữ liệu thực tế IEEE-CIS Fraud Detection. |
| **Tháng 3 (12/2026)** | Thiết kế và huấn luyện kiến trúc 2 tầng (Isolation Forest, LSTM), hệ thống Rule-based baseline và các mô hình đối sánh (LOF, LR, DT, RF, XGBoost) trên Google Colab. |
| **Tháng 4 (01/2027)** | Xây dựng dịch vụ backend FastAPI, bảng điều khiển React + D3.js, quy trình đề xuất hướng xử lý sau phát hiện và đóng gói Docker Compose trên DigitalOcean. |
| **Tháng 5 (02/2027)** | Thực nghiệm đánh giá toàn diện ở 3 cấp (Tầng 1, Tầng 2, Đầu cuối), phân tích hiệu năng và thời gian xử lý, viết bản thảo các chương luận văn. |
| **Tháng 6 (03/2027)** | Hoàn thiện cuốn luận văn, kiểm thử hệ thống demo hoàn chỉnh và chuẩn bị bảo vệ trước Hội đồng. |

---

*Học viên thực hiện: Nguyễn Huỳnh Thanh Triết (MSHV: 8480101250013)*  
*Giảng viên hướng dẫn: TS. Huỳnh Đệ Thủ — TS. Phạm Công Thành*  
*Chuyên ngành: Khoa học máy tính (Khóa 2025–2027) — Trường Đại học Quốc tế Sài Gòn (SIU)*
