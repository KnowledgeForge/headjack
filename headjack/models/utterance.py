from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Generator, Optional, Set, Type
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from headjack.models.utils import Stringable


@dataclass
class Utterance:
    utterance_: "Stringable"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    parent_: Optional["Utterance"] = None
    id: UUID = field(default_factory=uuid4)
    marker: ClassVar[str] = ""

    def __post_init__(self):
        self.session = self.parent_ and self.parent_.session

    @property
    def parent(self):
        return self.parent_

    @parent.setter
    def parent(self, parent: "Utterance"):
        if parent is not None:
            self.session = parent.session
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

    marker = "User: "


@dataclass
class Observation(Utterance):
    """
    Value produced from a tool
    """

    marker = "Observation: "
    consider_answer: bool = False


@dataclass
class Action(Utterance):
    """
    Value from an agent for using a tool
    """

    marker = "Action: "


@dataclass
class Thought(Utterance):
    """
    Value produced from an agent
    """

    marker = "Thought: "


@dataclass
class Answer(Utterance):
    """
    Final answer value produced from an agent
    """

    marker = "Answer: "
