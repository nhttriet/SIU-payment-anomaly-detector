# payment-anomaly-detector

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
| 1 | **Micro Fraud / Card Testing** | Bot thử hàng nghìn giao dịch nhỏ (< 200) để dò thẻ còn hiệu lực — khó phát hiện vì giá trị thấp |
| 2 | **High-value Fraud** | Giao dịch giá trị lớn bất thường (> 20,000) — dấu hiệu tài khoản bị chiếm quyền hoặc gian lận có chủ đích |

### Tại sao Rule-based không đủ?

- Attacker dễ dàng thay đổi pattern để né rule
- Cần update thủ công liên tục
- Thường phát hiện quá trễ sau khi thiệt hại đã xảy ra

---

## 3. Mục tiêu

Xây dựng hệ thống tự động phát hiện và phân loại bất thường theo thời gian thực, không phụ thuộc rule cứng, có khả năng học pattern và cảnh báo sớm — đồng thời trực quan hóa kết quả để ops team có thể drill-down nguyên nhân ngay trên dashboard.

---

## 4. Bài toán: Phân loại 3 nhãn

```
Class 0 → Normal           : Giao dịch bình thường
Class 1 → Micro Fraud      : Fraud + Amount < 200 (card testing, dò thẻ)
Class 2 → High-value Fraud : Fraud + Amount > 20,000 (giao dịch lớn bất thường)
```

---

## 5. Dataset

- **Nguồn:** Credit Card Fraud Detection Dataset 2023 (Kaggle)
- **Link:** kaggle.com/datasets/nelgiriyewithana/credit-card-fraud-detection-dataset-2023
- **Số lượng:** 568,630 giao dịch thẻ tín dụng thực tế năm 2023
- **Bảo mật:** Đã anonymized, V1–V28 đã qua PCA
- **Null values:** Không có

### Phân phối sau tái nhãn

| Class | Mô tả | Số lượng |
|---|---|---|
| 0 | Normal | 284,315 |
| 1 | Micro Fraud (Amount < 200) | 1,725 |
| 2 | High-value Fraud (Amount > 20,000) | 47,739 |

> **Lưu ý:** Dataset gốc đã được balance nhân tạo (50/50). Em tái nhãn Class 1 thành 3 nhóm dựa trên giá trị Amount, phù hợp với thực tế nghiệp vụ thanh toán NAPAS tại ACB.

---

## 6. Kiến trúc đề xuất — Pipeline 2 tầng

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
│  LSTM + Softmax       │ ──── Class 1 / Class 2
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

1. **Kiến trúc pipeline 2 tầng** kết hợp Isolation Forest + LSTM — vừa đảm bảo tốc độ realtime vừa phân loại được loại bất thường cụ thể
2. **Bộ nhãn 3 lớp** tự xây dựng dựa trên đặc trưng Amount, phù hợp với thực tế nghiệp vụ thanh toán
3. **So sánh thực nghiệm** nhiều phương pháp (IF, LOF, RF, XGBoost, LSTM) trên cùng dataset
4. **Dashboard tương tác** (React + D3.js) giúp ops team drill-down nguyên nhân, không chỉ đơn thuần cảnh báo
5. **Toàn bộ hệ thống đóng gói Docker**, có thể deploy thực tế

---

## 9. Metrics đánh giá

- Precision, Recall, F1-score (per class)
- AUC-ROC
- Latency pipeline (transactions/second)
- False Positive Rate

---

## 10. Timeline dự kiến (6 tháng)

| Tháng | Nội dung |
|---|---|
| 1 | Nghiên cứu lý thuyết, setup môi trường, EDA |
| 2 | Tái nhãn dataset, xây dựng pipeline ingestion + feature engineering |
| 3 | Train & tune ML models, đánh giá metrics |
| 4 | Xây dựng React + D3.js dashboard |
| 5 | Tích hợp end-to-end + viết luận văn |
| 6 | Hoàn thiện, demo, bảo vệ |

---

*Chương trình: Thạc sĩ Khoa học Máy tính*
