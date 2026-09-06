"""Trích xuất đặc trưng cho dữ liệu log thanh toán."""


def extract_features(raw_log: dict) -> dict:
    """Trả về các feature dùng cho mô hình phát hiện bất thường."""
    return {
        "api_path": raw_log.get("duong_dan_api"),
        "request_size": raw_log.get("kich_thuoc_yeu_cau"),
        "response_size": raw_log.get("kich_thuoc_phan_hoi"),
        "amount": raw_log.get("so_tien"),
        "device_id": raw_log.get("ma_thiet_bi"),
        "ip": raw_log.get("dia_chi_ip"),
    }
