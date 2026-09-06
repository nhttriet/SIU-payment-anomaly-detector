"""API lấy log theo README."""

from fastapi import APIRouter

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("")
def get_logs() -> dict:
    return {"status": "not_implemented"}
