from typing import Any, Dict
from uuid import uuid4

import jwt

from headjack.config import get_headjack_secret


def decode_token(access_token: str) -> Dict[str, Any]:
    return jwt.decode(access_token, get_headjack_secret(), algorithms=["HS256"])


def get_access_token():
    return jwt.encode({"session_id": str(uuid4())}, get_headjack_secret(), algorithm="HS256")
