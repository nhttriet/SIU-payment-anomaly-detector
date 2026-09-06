"""Entry point cho FastAPI theo README."""

from fastapi import FastAPI

app = FastAPI(title="Payment Anomaly Detector")


@app.get("/")
def read_root() -> dict:
    return {"message": "Payment Anomaly Detector API"}
