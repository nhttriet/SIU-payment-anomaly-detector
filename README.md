
# payment-anomaly-detector

## Xây dựng hệ thống phát hiện bất thường trong hệ thống thanh toán liên quan đến cờ bạc trực tuyến sử dụng học máy và trực quan hóa tương tác

---

## 1. Bối cảnh

Thanh toán điện tử tại Việt Nam đang tăng trưởng mạnh qua hạ tầng NAPAS với hàng triệu giao dịch mỗi ngày. Song song đó, các trang cờ bạc trực tuyến đang lợi dụng hệ thống thanh toán theo cơ chế tinh vi:

```
1. Nhà cái thu mua nhiều tài khoản ngân hàng "chân rơm"
2. Nhà cái đánh cắp token xác thực → crawl API lấy lịch sử giao dịch liên tục
3. Người dùng đặt cược chẵn/lẻ → chuyển tiền nhỏ (1k–10k) vào tài khoản chân rơm
4. Nhà cái đọc số cuối mã giao dịch → xác định kết quả chẵn/lẻ
5. Trả thưởng qua website riêng, không qua hệ thống ngân hàng
```

---

## 2. Vấn đề

Hệ thống giám sát truyền thống (dựa trên quy tắc cứng) không phát hiện được vì:

* Kẻ tấn công thay đổi cách thức liên tục để né quy tắc
* Số tiền nhỏ (1k–10k) không kích hoạt ngưỡng cảnh báo thông thường
* Token xác thực hợp lệ nên không bị chặn ở tầng bảo mật
* Phải cập nhật quy tắc thủ công, phát hiện thường quá trễ

---

## 3. Mục tiêu

Xây dựng hệ thống tự động phát hiện và phân loại bất thường từ **log tại cổng API** — không phụ thuộc quy tắc cứng — đồng thời trực quan hóa kết quả để nhóm vận hành có thể xem chi tiết nguyên nhân ngay trên bảng điều khiển.

---

## 4. Phân loại 3 nhãn

```
Nhãn 0 → Bình thường         : Tài khoản hoạt động bình thường
                                Thiết bị ổn định, truy cập đa dạng,
                                số tiền giao dịch đa dạng, thời gian tự nhiên

Nhãn 1 → Lạm dụng token      : Token xác thực bị đánh cắp
                                Kẻ tấn công dùng token để liên tục lấy
                                lịch sử giao dịch, IP và thiết bị bất thường,
                                không có hành vi sử dụng app bình thường

Nhãn 2 → Tài khoản chân rơm  : Tài khoản bị lợi dụng làm cổng nhận tiền cờ bạc
                                Nhận hàng trăm giao dịch nhỏ 1k–10k/ngày
                                từ nhiều người khác nhau, liên tục
```

---

## 5. Dữ liệu — Log tại cổng API (19 trường)

Tự xây dựng dữ liệu mô phỏng từ 1 nguồn log duy nhất tại cổng API:

| #  | Tên trường             | Mô tả                                                                 |
| -- | ------------------------- | ----------------------------------------------------------------------- |
| 1  | `thoi_gian`             | Thời gian gửi yêu cầu (chính xác đến mili giây)                |
| 2  | `ma_yeu_cau`            | Mã định danh duy nhất của mỗi yêu cầu                           |
| 3  | `ma_theo_doi`           | Mã theo dõi toàn bộ luồng xử lý                                  |
| 4  | `ma_nguoi_dung`         | Mã tài khoản người dùng                                           |
| 5  | `ma_token`              | Mã băm của token xác thực (không lưu token thật)                |
| 6  | `ma_thiet_bi`           | Thiết bị gửi yêu cầu                                               |
| 7  | `dia_chi_ip`            | Địa chỉ IP nguồn                                                    |
| 8  | `thong_tin_trinh_duyet` | Thông tin trình duyệt / ứng dụng                                   |
| 9  | `duong_dan_api`         | API được gọi (/lich-su-giao-dich, /chuyen-tien,...)                 |
| 10 | `phuong_thuc`           | Phương thức gọi (GET / POST)                                        |
| 11 | `kich_thuoc_yeu_cau`    | Kích thước yêu cầu (bytes)                                         |
| 12 | `tai_khoan_gui`         | Mã tài khoản gửi tiền                                              |
| 13 | `tai_khoan_nhan`        | Mã tài khoản nhận tiền                                             |
| 14 | `so_tien`               | Số tiền giao dịch                                                    |
| 15 | `loai_giao_dich`        | Loại giao dịch (chuyển khoản / thanh toán / truy vấn)             |
| 16 | `ma_http`               | Mã phản hồi HTTP (200, 401, 403,...)                                 |
| 17 | `ma_nghiep_vu`          | Mã kết quả nghiệp vụ (00=thành công, 05=không đủ số dư,...) |
| 18 | `thoi_gian_xu_ly`       | Thời gian xử lý yêu cầu (mili giây)                               |
| 19 | `kich_thuoc_phan_hoi`   | Kích thước phản hồi (bytes)                                        |

### Đặc trưng theo từng nhãn

| Trường                           | Bình thường | Lạm dụng token              | Tài khoản chân rơm     |
| ---------------------------------- | -------------- | ----------------------------- | -------------------------- |
| Đường dẫn API                  | Đa dạng      | /lich-su-giao-dich liên tục | /chuyen-tien liên tục    |
| Thiết bị                         | Ổn định     | Thay đổi / bất thường    | Nhiều thiết bị          |
| Địa chỉ IP                      | Ổn định     | IP lạ, thay đổi liên tục | Nhiều IP                  |
| Số tiền                          | Đa dạng      | Không có (chỉ truy vấn)   | 1,000 – 10,000 cố định |
| Tài khoản nhận                  | Đa dạng      | Không có                    | Cố định (chân rơm)    |
| Khoảng cách giữa các yêu cầu | Tự nhiên     | Vài giây/lần               | Liên tục                 |

> Dữ liệu được xây dựng dựa trên kinh nghiệm thực tế làm việc với hệ thống thanh toán NAPAS tại ACB.

---

## 6. Kiến trúc hệ thống

### Luồng vận hành (MLOps)

```
[Máy local]                [Google Colab]              [DigitalOcean]
     │                           │                            │
Generate                    Mount Drive                  Load model
synthetic data    ──────►   Pull code từ Git   ──────►   FastAPI serve
     │                      Train IF + LSTM               REST API
Push lên Git                Save model vào                   │
                            Google Drive                      │
                                                        React + D3.js
                                                          Dashboard
```

> **Lưu ý:** Kafka và Filebeat chỉ xuất hiện trong sơ đồ kiến trúc luận văn để thể hiện khả năng mở rộng realtime — không cần dựng thật trong phạm vi đề tài.

### Quy trình xử lý 2 tầng

```
Log cổng API (CSV)
        │
        ▼
Trích xuất đặc trưng
(tần suất gọi API, khoảng cách yêu cầu,
 mức độ ổn định thiết bị/IP, pattern số tiền,...)
        │
        ▼
┌─────────────────────────┐
│  Tầng 1                 │
│  Isolation Forest       │ ──── Bình thường → bỏ qua
│  (phát hiện nhanh)      │
└─────────────────────────┘
        │ Bất thường
        ▼
┌─────────────────────────┐
│  Tầng 2                 │
│  LSTM + Softmax         │ ──── Nhãn 1 / Nhãn 2
│  (phân loại chi tiết)   │
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  Bảng điều khiển        │
│  React + D3.js          │ ──── Trực quan hóa + Xem chi tiết
└─────────────────────────┘
```

### Chi tiết từng tầng

| Tầng   | Mô hình        | Vai trò                        | Mô hình so sánh     |
| ------- | ---------------- | ------------------------------- | ---------------------- |
| Tầng 1 | Isolation Forest | Lọc nhanh bất thường        | LOF                    |
| Tầng 2 | LSTM + Softmax   | Phân loại loại bất thường | Random Forest, XGBoost |

---

## 7. Hướng xử lý sau phát hiện

| Phát hiện        | Hành động                                                      | Giải thích                                                                                                     |
| ------------------ | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Nhãn 1 mức nhẹ  | Giới hạn tốc độ gọi API                                     | Làm chậm yêu cầu, tránh chặn nhầm người dùng thật                                                     |
| Nhãn 1 mức nặng | Vô hiệu hóa token + cảnh báo nhóm bảo mật                 | Token bị lạm dụng nghiêm trọng cần xử lý ngay                                                            |
| Nhãn 2            | Đóng băng tài khoản + báo cáo nhóm tuân thủ             | Vi phạm Luật Phòng chống rửa tiền 2022, cần báo cáo giao dịch đáng ngờ lên Ngân hàng Nhà nước |
| Nhãn 1 + Nhãn 2  | Vô hiệu hóa token + Đóng băng tài khoản + Báo cáo khẩn | Trường hợp nghiêm trọng, leo thang lên cả nhóm bảo mật và tuân thủ                                  |

---

## 8. Cấu trúc thư mục

```
payment-anomaly-detector/
│
├── data/                               # Dữ liệu
│   ├── generate_data.py                # Script tạo synthetic log
│   ├── raw/                            # Log gốc (.gitignore)
│   └── processed/                      # Log đã xử lý (.gitignore)
│
├── notebooks/                          # Google Colab notebooks
│   ├── 01_eda.ipynb                    # Khám phá dữ liệu
│   ├── 02_feature_engineering.ipynb    # Trích xuất đặc trưng
│   ├── 03_train_isolation_forest.ipynb # Huấn luyện tầng 1
│   └── 04_train_lstm.ipynb             # Huấn luyện tầng 2
│
├── ml/                                 # Học máy
│   ├── features.py                     # Trích xuất đặc trưng
│   ├── isolation_forest.py             # Mô hình tầng 1
│   ├── lstm_model.py                   # Mô hình tầng 2
│   └── saved_models/                   # Trọng số mô hình (.gitignore)
│       ├── if_v1.pkl
│       └── lstm_v1.pt
│
├── backend/                            # FastAPI
│   ├── main.py                         # Điểm khởi chạy
│   ├── routers/
│   │   ├── predict.py                  # API dự đoán
│   │   └── logs.py                     # API lấy log
│   ├── services/
│   │   └── model_service.py            # Tải và chạy mô hình
│   └── requirements.txt
│
├── frontend/                           # React + D3.js
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx           # Trang chính
│   │   │   ├── AnomalyChart.jsx        # Biểu đồ D3.js
│   │   │   ├── LogTable.jsx            # Bảng log
│   │   │   └── AlertPanel.jsx          # Bảng cảnh báo
│   │   └── App.jsx
│   └── package.json
│
├── docs/                               # Tài liệu
│   ├── architecture.png                # Sơ đồ kiến trúc
│   └── thesis/                         # Bản thảo luận văn
│
├── docker-compose.yml                  # Đóng gói toàn hệ thống
├── .gitignore
└── README.md
```

---

## 9. Công nghệ sử dụng

| Tầng                  | Công nghệ                                           |
| ---------------------- | ----------------------------------------------------- |
| Tạo dữ liệu         | Python + Faker                                        |
| Huấn luyện mô hình | Google Colab (GPU miễn phí)                         |
| Mô hình học máy    | scikit-learn (Isolation Forest, LOF) + PyTorch (LSTM) |
| Mô hình so sánh     | XGBoost, Random Forest                                |
| Lưu trữ mô hình    | Google Drive                                          |
| API backend            | FastAPI                                               |
| Giao diện             | React + D3.js                                         |
| Triển khai            | Docker Compose + DigitalOcean                         |

---

## 10. Đóng góp chính

1. **Phân tích và mô hình hóa** cơ chế lợi dụng hệ thống thanh toán của cờ bạc trực tuyến — bài toán thực tế tại Việt Nam
2. **Chỉ cần 1 nguồn log** tại cổng API — phát hiện được cả 2 loại tấn công
3. **Kiến trúc xử lý 2 tầng** kết hợp Isolation Forest + LSTM
4. **So sánh thực nghiệm** nhiều phương pháp (Isolation Forest, LOF, Random Forest, XGBoost, LSTM)
5. **Hướng xử lý rõ ràng** theo từng loại bất thường — từ giới hạn tốc độ đến đóng băng tài khoản và báo cáo cơ quan quản lý
6. **Bảng điều khiển tương tác** React + D3.js — xem chi tiết từng sự kiện bất thường
7. **Toàn bộ hệ thống đóng gói Docker** , triển khai trên DigitalOcean

---

## 11. Đánh giá hiệu quả

* Độ chính xác, Độ phủ, F1-score (theo từng nhãn)
* Diện tích dưới đường cong ROC (AUC-ROC)
* Tốc độ xử lý (yêu cầu/giây)
* Tỷ lệ cảnh báo nhầm (False Positive Rate)

---

## 12. Kế hoạch thực hiện (6 tháng)

| Tháng | Nội dung                                                                            |
| ------ | ------------------------------------------------------------------------------------ |
| 1      | Nghiên cứu lý thuyết, phân tích cơ chế tấn công, thiết kế cấu trúc log |
| 2      | Tạo dữ liệu mô phỏng, trích xuất đặc trưng                                 |
| 3      | Huấn luyện và tinh chỉnh mô hình trên Colab, đánh giá hiệu quả           |
| 4      | Xây dựng bảng điều khiển React + D3.js                                         |
| 5      | Tích hợp toàn hệ thống + viết luận văn                                       |
| 6      | Hoàn thiện, demo, bảo vệ                                                         |

---

*Học viên thực hiện: Nguyễn Huỳnh Thanh Triết*
*Giảng viên hướng dẫn: TS.Huỳnh Đệ Thủ*
*Chương trình: Thạc sĩ Khoa học Máy tính*
