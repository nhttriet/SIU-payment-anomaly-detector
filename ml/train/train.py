"""Huấn luyện mô hình phát hiện bất thường theo kiến trúc 2 tầng."""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    print(f"Project base: {base}")
    print("Bước 1: chuẩn bị dữ liệu")
    print("Bước 2: huấn luyện Isolation Forest")
    print("Bước 3: huấn luyện LSTM")
    print("Bước 4: lưu model vào ml/saved_models")


if __name__ == "__main__":
    main()
