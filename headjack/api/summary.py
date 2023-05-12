import logging

from fastapi import APIRouter

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("/")
def generate_a_summary():
    return ""
