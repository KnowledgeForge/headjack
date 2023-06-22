import json
import logging
import re
from typing import Any, Generator, Optional, Set, Type, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from headjack.logging import UTTERANCE_LOG_LEVEL

_logger = logging.getLogger("headjack")


class Utterance(BaseModel):
    utterance: str
    # timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    parent: Optional["Utterance"] = None
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    marker: Optional[str] = Field(default="")
    source: Optional[str] = None
    direct_response: bool = False
    metadata: Optional[dict] = None
    notes: str = ""

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
        truncate_utterances: Optional[Set[Type["Utterance"]]] = None,
        truncation_length: int = 150,
    ) -> str:
        history = []
        n = n or float("inf")  # type: ignore
        for utterance in self.history():
            if truncate_utterances is None or type(utterance) in truncate_utterances:
                utterance_strs = re.split(r"[' ']+", str(utterance.utterance).replace("\n", " \n"))
                if len(utterance_strs) > truncation_length:
                    utterance_str = utterance.marker.replace(':', ' (truncated):') + " ".join(
                        utterance_strs[: truncation_length // 2]
                        + ["..."]
                        + utterance_strs[-(truncation_length // 2) :],  # noqa: E203
                    )
                else:
                    utterance_str = str(utterance)
                history.append(utterance_str+(f" Note (users should never see note information): {utterance.notes}") if utterance.notes else "")
            else:
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
            _logger.log(UTTERANCE_LOG_LEVEL, self._log_str())
            self._set_logged(True)
        for utterance in self.history():
            if not utterance._logged:
                utterance.log()


class User(Utterance):
    marker = "User: "


class Observation(Utterance):
    marker = "Observation: "
    direct_response = True


class Action(Utterance):
    marker = "Action: "


class Thought(Utterance):
    marker = "Thought: "


class Answer(Utterance):
    marker = "Answer: "

class Response(Utterance):
    marker = "Response: "


UTTERANCES = {User, Observation, Action, Thought, Answer, Response}
