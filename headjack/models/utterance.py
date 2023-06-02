from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Generator, Optional, Set, Type
from uuid import UUID, uuid4

from headjack.models.utils import required_value

if TYPE_CHECKING:
    from headjack.models.utils import Stringable


@dataclass
class Utterance:
    utterance_: "Stringable"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: str = ""
    parent_: Optional["Utterance"] = None
    id: UUID = field(default_factory=uuid4)
    session_: Optional["Session"] = field(default=None, init=False)
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
    def session(self):
        if self.session_ is not None:
            return self.session_
        if self.parent is not None:
            return self.parent.session
        return None

    @session.setter
    def session(self, session: "Session"):
        self.session_ = session

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
    tool: "Tool" = field(default_factory=required_value("`tool` is required for an Observation.", tool_model.Tool))
    consider_answer: bool = False


@dataclass
class Action(Utterance):
    """
    Value from an agent for using a tool
    """

    utterance_: dict
    marker = "Action: "
    agent: "Agent" = field(default_factory=required_value("`agent` is required for an Action.", agent_model.Agent))


@dataclass
class Feedback(Utterance):
    """
    An utterance from a tool suggesting the agent make changes to its action
    """

    marker = "Feedback: "
    tool: "Tool" = field(default_factory=required_value("`tool` is required for an Observation.", tool_model.Tool))
    retries: int = 0


@dataclass
class Thought(Utterance):
    """
    Value produced from an agent
    """

    agent: "Agent" = field(default_factory=required_value("`agent` is required for a Thought.", agent_model.Agent))
    marker = "Thought: "


@dataclass
class Answer(Utterance):
    """
    Final answer value produced from an agent
    """

    agent: "Agent" = field(default_factory=required_value("`agent` is required for a Answer.", agent_model.Agent))
    marker = "Answer: "
