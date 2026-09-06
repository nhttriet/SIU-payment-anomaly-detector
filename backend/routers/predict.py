"""API dự đoán theo kiến trúc README."""

from fastapi import APIRouter

router = APIRouter(prefix="/predict", tags=["predict"])


@router.get("")
def predict() -> dict:
    return {"status": "not_implemented"}
