from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Generator, Optional, Set, Type
from uuid import uuid4

from pydantic.types import Json


@dataclass
class Utterance:
    utterance_: str
    timestamp: str = field(default_factory=lambda: str(datetime.utcnow()))
    parent_: Optional["Utterance"] = None
    id: str = field(default_factory=lambda: str(uuid4()))
    marker: Optional[str] = None
    marker_: ClassVar[str] = ""

    def __post_init__(self):
        self.marker = self.marker or self.marker_

    @property
    def parent(self):
        return self.parent_

    @parent.setter
    def parent(self, parent: "Utterance"):
        if parent is not None:
            self.parent_ = parent

    def __str__(self):
        return self.marker + self.utterance

    def history(self, n: Optional[int] = None) -> Generator:
        n_ = n or float("inf")  # type: ignore
        curr = self
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
        utterance_kinds = utterance_kinds or {User, Answer}
        for utterance in self.history():
            if type(utterance) in utterance_kinds:
                history.append(utterance)
            if len(history) == n:
                break

        history = history[::-1]
        return "\n".join(str(u) for u in history) + "\n"

    @property
    def utterance(self):
        return str(self.utterance_)


@dataclass
class User(Utterance):
    """
    Utterance from a user
    """

    utterance_: str
    marker_ = "User: "


@dataclass
class Observation(Utterance):
    """
    Value produced from a tool
    """

    utterance_: Json
    marker_ = "Observation: "


@dataclass
class Action(Utterance):
    """
    Value from an agent for using a tool
    """

    utterance_: Json
    marker_ = "Action: "


@dataclass
class Thought(Utterance):
    """
    Value produced from an agent
    """

    utterance_: str
    marker_ = "Thought: "


@dataclass
class Answer(Utterance):
    """
    Answer generated from agent
    """

    utterance_: str
    marker_ = "Answer: "


@dataclass
class Response(Utterance):
    """
    Responses generated from an agent when there were issues encountered
    """

    utterance_: str
    marker_ = "Response: "
