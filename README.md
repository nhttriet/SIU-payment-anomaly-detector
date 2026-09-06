# Đề tài Khoá luận Thạc sĩ

## Xây dựng hệ thống phát hiện và phân loại bất thường trong log hệ thống thanh toán sử dụng học máy và trực quan hóa tương tác

> **Anomaly Detection and Classification in Payment System Logs using Machine Learning and Interactive Visualization**

---

## 1. Bối cảnh

Thanh toán điện tử tại Việt Nam đang tăng trưởng mạnh, đặc biệt qua hạ tầng NAPAS với hàng triệu giao dịch mỗi ngày. Sự phát triển này kéo theo các rủi ro ngày càng tinh vi hơn mà các hệ thống giám sát truyền thống (rule-based, threshold cứng) không còn đủ khả năng phát hiện kịp thời.

---

## 2. Vấn đề

Các hệ thống thanh toán hiện đại đang đối mặt với nhiều dạng tấn công và bất thường tinh vi:

| # | Loại bất thường | Mô tả |
|---|---|---|
| 1 | **Spam API từ ứng dụng cờ bạc** | Bot liên tục tạo giao dịch nhỏ có chu kỳ để khai thác lịch sử transaction ID/timestamp nhằm dự đoán kết quả chẵn lẻ — gây tốn tài nguyên hệ thống và vi phạm compliance |
| 2 | **Transaction Looping** | Cùng một giao dịch bị lặp lại bất thường do bug hoặc cố ý, gây sai lệch số dư và khó đối soát |
| 3 | **Off-hour Suspicious Transaction** | Giao dịch giá trị lớn xảy ra lúc 2–4 giờ sáng từ tài khoản bình thường — dấu hiệu tài khoản bị chiếm quyền |
| 4 | **Card Testing / Credential Stuffing** | Bot thử hàng nghìn thẻ với số tiền nhỏ để tìm thẻ còn hiệu lực |

### Tại sao Rule-based không đủ?

- Attacker dễ dàng thay đổi pattern để né rule
- Cần update thủ công liên tục
- Thường phát hiện quá trễ sau khi thiệt hại đã xảy ra

---

## 3. Mục tiêu

Xây dựng hệ thống tự động phát hiện và phân loại bất thường theo thời gian thực, không phụ thuộc rule cứng, có khả năng học pattern và cảnh báo sớm — đồng thời trực quan hóa kết quả để ops team có thể drill-down nguyên nhân ngay trên dashboard.

---

## 4. Bài toán: Phân loại 4 lớp

```
Class 0 → Normal              : Giao dịch bình thường
Class 1 → Spam API            : Bot cờ bạc, tấn công có chu kỳ
Class 2 → Transaction Looping : Giao dịch lặp bất thường
Class 3 → Off-hour Anomaly    : Giao dịch đáng ngờ ngoài giờ
```

---

## 5. Kiến trúc đề xuất — Pipeline 2 tầng

```
Log Stream (realtime)
        │
        ▼
┌───────────────────────┐
│  Tầng 1               │
│  Isolation Forest     │ ──── Normal (0) → bỏ qua
│  (phát hiện nhanh)    │
└───────────────────────┘
        │ Anomaly
        ▼
┌───────────────────────┐
│  Tầng 2               │
│  LSTM + Softmax       │ ──── Class 1 / 2 / 3
│  (phân loại loại)     │
└───────────────────────┘
        │
        ▼
┌───────────────────────┐
│  Dashboard            │
│  React + D3.js        │ ──── Visualize + Drill-down
└───────────────────────┘
```

### Chi tiết từng tầng

| Tầng | Mô hình | Vai trò | Baseline so sánh |
|---|---|---|---|
| Tầng 1 | Isolation Forest | Lọc nhanh anomaly realtime | LOF |
| Tầng 2 | LSTM + Softmax | Phân loại loại bất thường | Random Forest, XGBoost |

---

## 6. Dataset

- **Nguồn:** Credit Card Fraud Detection Dataset 2023 (Kaggle)
- **Số lượng:** 550,000+ giao dịch thẻ tín dụng thực tế năm 2023
- **Bảo mật:** Đã anonymized, bảo vệ thông tin cá nhân
- **Nhãn gốc:** 2 nhãn (normal / fraud)
- **Mở rộng:** Tái nhãn thành 4 lớp dựa trên kinh nghiệm thực tế với hệ thống thanh toán NAPAS tại ACB

---

## 7. Tech Stack

| Layer | Technology |
|---|---|
| Log Ingestion | Filebeat + Kafka |
| Log Parsing | Drain3 (Python) |
| ML Models | scikit-learn (Isolation Forest, LOF) + PyTorch (LSTM) |
| Baseline | XGBoost, Random Forest |
| Backend API | FastAPI |
| Frontend | React + D3.js |
| Deployment | Docker Compose |

---

## 8. Đóng góp chính

1. **Kiến trúc pipeline 2 tầng** kết hợp Isolation Forest + LSTM — vừa đảm bảo tốc độ realtime vừa phân loại được loại tấn công cụ thể
2. **Bộ nhãn 4 lớp** tự xây dựng phù hợp với thực tế hệ thống thanh toán Việt Nam
3. **So sánh thực nghiệm** nhiều phương pháp (IF, LOF, RF, XGBoost, LSTM) trên cùng dataset
4. **Dashboard tương tác** (React + D3.js) giúp ops team drill-down nguyên nhân, không chỉ đơn thuần cảnh báo
5. **Toàn bộ hệ thống đóng gói Docker**, có thể deploy thực tế

---

## 9. Metrics đánh giá

- Precision, Recall, F1-score (per class)
- AUC-ROC
- Latency pipeline (log/second)
- False Positive Rate

---

## 10. Timeline dự kiến (6 tháng)

| Tháng | Nội dung |
|---|---|
| 1 | Nghiên cứu lý thuyết, setup môi trường, data exploration |
| 2 | Xây dựng pipeline ingestion + log parsing + feature engineering |
| 3 | Train & tune ML models, đánh giá metrics |
| 4 | Xây dựng React + D3.js dashboard |
| 5 | Tích hợp end-to-end + viết luận văn |
| 6 | Hoàn thiện, demo, bảo vệ |

---

*Chương trình: Thạc sĩ Khoa học Máy tính*
