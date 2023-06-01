"""
Pydantic models
"""
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class UtteranceType(str, Enum):
    user = "user"
    observation = "observation"
    action = "action"
    thought = "thought"
    answer = "answer"


class Utterance(BaseModel):
    type: UtteranceType
    timestamp: datetime
    context: str = ""
