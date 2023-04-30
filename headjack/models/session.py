import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    Optional,
    Set,
    Type,
    Union,
    TYPE_CHECKING, cast
)
from uuid import UUID, uuid4

class SessionStatus(Enum):
    DISCONNECTED = "DISCONNECTED"
    LIVE = "LIVE"
    TIMEOUT = "TIMEOUT"

if TYPE_CHECKING:
    from headjack.models.utterance import Action, Observation, Thought, Answer, Utterance, User
    from headjack.models.agent import Agent

@dataclass
class Session:
    agent: "Agent"  # sessions are with an agent
    agent_utterances: Set[Union[Type[Action], Type[Observation], Type[Thought], Type[Answer]]] = field(
        default_factory=lambda: {Action, Observation, Thought, Answer},
    )  # this determines how verbose the agent will be
    session_id: UUID = field(default_factory=uuid4)
    status: SessionStatus = SessionStatus.LIVE
    utterance: Optional[Utterance] = field(default=None, init=False)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    timeout: int = 60 * 10
    sessions: ClassVar[Dict[UUID, "Session"]] = {}

    def __post_init__(self):
        Session.sessions[self.session_id] = self

    def check_quit(self, utterance: Optional[Utterance]) -> bool:
        if utterance is None or utterance.utterance.strip() in ("", "quit", "exit"):
            self.status = SessionStatus.DISCONNECTED
            return True
        return False

    async def __call__(self, input: Optional[str]):
        # wait for user input
        user: Optional[User] = User(input) if input is not None else input

        # session is disconnected if a user utterance is none or empty
        if self.check_quit(user):
            return
        user = cast(User, user)
        user.session = self
        user.parent = cast(Utterance, self.utterance)
        self.utterance = user
        responding = asyncio.create_task(self.agent(self.utterance))
        # agent gives all it's utterances in response to the user utterance
        while (not responding.done()) or (not self.agent.queue.empty()):
            response = await self.agent.queue.get()
            if self.check_quit(response):
                self.agent.queue.task_done()
                return
            self.utterance = response
            # only send utterances we're asked to send
            if type(response) in self.agent_utterances:
                yield response
            self.agent.queue.task_done()
        return
