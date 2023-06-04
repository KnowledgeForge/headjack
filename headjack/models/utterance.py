from typing import Generator, Optional, Set, Type

from pydantic import BaseModel, Field
from pydantic.types import Json


class Utterance(BaseModel):
    utterance: str
    # timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    parent_: Optional["Utterance"] = None
    # id: Optional[UUID] = Field(default_factory=uuid4)
    marker: Optional[str] = Field(default="")

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
        n_ = n or float("inf")
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


class User(Utterance):
    utterance: str
    marker = "User: "


class Observation(Utterance):
    utterance: Json
    marker = "Observation: "


class Action(Utterance):
    utterance: Json
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
