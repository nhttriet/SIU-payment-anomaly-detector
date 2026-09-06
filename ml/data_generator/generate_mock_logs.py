"""Script tạo dữ liệu mô phỏng theo 3 nhãn: bình thường, lạm dụng token, chân rơm."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path


def generate_mock_logs(output_path: str = "data/raw/payment_logs.jsonl", rows: int = 2000) -> None:
    """Tạo dữ liệu mô phỏng với 19 trường log như trong đề xuất."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    records = []
    base_time = datetime(2026, 1, 1, 8, 0, 0)

    for i in range(rows):
        ts = base_time + timedelta(seconds=i * 2)
        record = {
            "thoi_gian": ts.isoformat(),
            "ma_yeu_cau": f"req_{i:06d}",
            "ma_theo_doi": f"trace_{i:06d}",
            "ma_nguoi_dung": f"user_{(i % 120) + 1}",
            "ma_token": f"token_{(i % 80) + 1}",
            "ma_thiet_bi": f"device_{(i % 12) + 1}",
            "dia_chi_ip": f"10.0.0.{(i % 64) + 1}",
            "thong_tin_trinh_duyet": "Chrome/124.0",
            "duong_dan_api": "/lich-su-giao-dich" if i % 3 == 0 else "/chuyen-tien",
            "phuong_thuc": "GET" if i % 3 == 0 else "POST",
            "kich_thuoc_yeu_cau": 800 + (i % 10) * 50,
            "tai_khoan_gui": f"acc_{(i % 50) + 1}",
            "tai_khoan_nhan": f"acc_{(i % 60) + 10}",
            "so_tien": 1000 + (i % 9) * 500,
            "loai_giao_dich": "chuyen_khoan",
            "ma_http": 200,
            "ma_nghiep_vu": "00",
            "thoi_gian_xu_ly": 120 + (i % 7) * 10,
            "kich_thuoc_phan_hoi": 900 + (i % 12) * 40,
            "label": "binh_thuong",
        }
        records.append(record)

    with output.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Đã tạo {len(records)} bản ghi tại {output}")


if __name__ == "__main__":
    generate_mock_logs()
