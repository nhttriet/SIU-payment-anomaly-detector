"""Mô hình tầng 2: LSTM + Softmax."""


class LSTMModel:
    """Khung mô hình LSTM theo README."""

    def __init__(self) -> None:
        self.name = "LSTM"

    def predict(self, sequences):
        return {"status": "not_implemented", "model": self.name, "sequences": sequences}
