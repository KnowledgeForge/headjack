import json
import logging
from typing import Any, Generator, Optional, Set, Type, Union
from uuid import uuid4

from pydantic import BaseModel, Field

_logger = logging.getLogger("uvicorn")


class Utterance(BaseModel):
    utterance: Any
    # timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    parent: Optional["Utterance"] = None
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    marker: Optional[str] = Field(default="")
    source: Optional[str] = None

    def _logged(self):
        return getattr(self, "__logged", False)

    def _set_logged(self, value: bool):
        object.__setattr__(self, "__logged", value)

    def __str__(self):
        return self.marker + str(self.utterance)

    def history(self, n: Optional[int] = None) -> Generator:
        n_ = n or float("inf")
        curr: Optional["Utterance"] = self
        while n_ > 0 and (curr is not None):
            yield curr
            curr = curr.parent
            n_ -= 1

    def convo(
        self,
        n: Optional[int] = None,
        utterance_kinds: Optional[Set[Type["Utterance"]]] = None,
    ) -> str:
        history = []
        n = n or float("inf")  # type: ignore
        utterance_kinds = utterance_kinds or set(Utterance.__subclasses__())
        for utterance in self.history():
            if type(utterance) in utterance_kinds:
                history.append(utterance)
            if len(history) == n:
                break

        history = history[::-1]
        return "\n".join(str(u) for u in history) + "\n"

    def _log_str(self) -> str:
        """Creates a string for logging the utterance"""
        return json.dumps(
            {
                "class": self.__class__.__name__,
                "id": self.id,
                "parent": self.parent and self.parent.id,
                "utterance": self.utterance,
            },
        )

    def log(self):
        """Logs all utterances that have not yet been logged"""
        if not self._logged():
            _logger.utterance(self._log_str())  # type: ignore
            self._set_logged(True)
        for utterance in self.history():
            if not utterance._logged:
                utterance.log()


class User(Utterance):
    utterance: str
    marker = "User: "


class Observation(Utterance):
    utterance: dict
    marker = "Observation: "


class Action(Utterance):
    utterance: Union[str, dict]
    marker = "Action: "


class Thought(Utterance):
    utterance: str
    marker = "Thought: "


class Answer(Utterance):
    utterance: str
    marker = "Answer: "


class Response(Utterance):
    utterance: str
    marker = "Response: "
