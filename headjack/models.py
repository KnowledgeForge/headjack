import asyncio
import inspect
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    Generator,
    List,
    Optional,
    Protocol,
    Set,
    Type,
    TypedDict,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID, uuid4

import lmql
from headjack.utils import add_source
from chromadb.utils import embedding_functions
from headjack.config import get_chroma_client

@dataclass
class VectorStore:
    collection_name: str

    def __post_init__(self):
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(self.collection_name, embedding_function=ef)


T = TypeVar("T")


def required_value(message: str, return_type: Type[T]) -> Callable[[], T]:
    def raise_message() -> T:
        raise ValueError(message)

    return raise_message


class Stringable(Protocol):
    def __str__(self) -> str:
        pass


SchemaDict = Dict[str, Union[Type[str], Type[int], "SchemaDict"]]


@dataclass
class ToolSchema:
    """
    Final answer value produced from an agent
    """

    schema_dict: Type[TypedDict]
    _compiled: bool = field(init=False, default=False)
    _body: Optional[str] = field(init=False, default=None)
    _where: Optional[str] = field(init=False, default=None)

    @property
    def body(self):
        self._compile()
        return self._body

    @property
    def code(self):
        self._compile()
        return cast(str, self.body).replace('\\"[', "").replace("]", "").replace('\\"', '"').strip()[1:-1]

    @property
    def where(self):
        self._compile()
        return self._where

    def _compile(self):
        if self._compiled:
            return
        schema_dict = self.schema_dict.__annotations__
        if not schema_dict:
            self._body = ""
            self._where = ""
            return
        where = []
        prefix = self.schema_dict.__name__ + "_"

        def _helper(schema, key, end=False):
            if schema == int:
                variable = (prefix + key).upper()
                where.append(f'INT({variable}) and STOPS_AT({variable}, ",")')
                return variable
            if schema == str:
                variable = (prefix + key).upper()
                where.append(f"""STOPS_AT({variable}, '"')""")
                return variable
            if not isinstance(schema, dict):
                raise Exception(f"Unnacceptable type in schema: `{schema}`")
            result = "{{"
            for idx, (key, value) in enumerate(schema.items()):
                if "[" in key or "]" in key:
                    raise Exception("schema keys cannot have `[` or `]`")
                variable = _helper(value, key=key, end=idx == len(schema))
                quote = '\\"' if value == str else ""
                result += f'\\"{key}\\": {quote}[{variable}], '
            result = result[:-2] + "}}"
            return result

        self._body = _helper(schema_dict, key="")
        self._where = " and ".join(where)


@dataclass
class Tool:
    default_description: ClassVar[str]
    default_ref_name: ClassVar[str]
    input_schema: ClassVar[ToolSchema]
    model_identifier: Optional[str] = None
    description_: Optional[str] = None
    ref_name_: Optional[str] = None
    max_uses_per_query: int = cast(int, float("inf"))

    @property
    def description(self):
        return self.description_ or self.default_description

    @property
    def ref_name(self):
        return self.ref_name_ or self.default_ref_name

    async def __call__(self, action: "Action") -> "Observation":
        raise NotImplementedError()


@dataclass
class Utterance:
    utterance_: Stringable
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
        n = n or float("inf")
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
    tool: Tool = field(default_factory=required_value("`tool` is required for an Observation.", Tool))


@dataclass
class Action(Utterance):
    """
    Value produced from a tool
    """

    utterance_: dict
    marker = "Action: "
    agent: "Agent" = field(default_factory=required_value("`agent` is required for an Action.", lambda: Agent()))


@dataclass
class Thought(Utterance):
    """
    Value produced from an agent
    """

    agent: "Agent" = field(default_factory=required_value("`agent` is required for a Thought.", lambda: Agent()))
    marker = "Thought: "


@dataclass
class Answer(Utterance):
    """
    Final answer value produced from an agent
    """

    agent: "Agent" = field(default_factory=required_value("`agent` is required for a Answer.", lambda: Agent()))
    marker = "Answer: "


class SessionStatus(Enum):
    DISCONNECTED = "DISCONNECTED"
    LIVE = "LIVE"
    TIMEOUT = "TIMEOUT"


@dataclass
class Session:
    agent: "Agent"  # sessions are with an agent
    agent_utterances: Set[Union[Type[Action], Type[Observation], Type[Thought], Type[Answer]]] = field(
        default_factory=lambda: {Action, Observation, Thought, Answer},
    )  # this determines how verbose the agent will be
    session_id: UUID = field(default_factory=uuid4)
    status: SessionStatus = SessionStatus.LIVE
    utterance: Optional[str] = field(default=None, init=False)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    timeout: int = 60 * 10
    sessions: ClassVar[Dict[UUID, "Session"]] = {}

    def __post_init__(self):
        Session.sessions[self.session_id] = self

    def check_quit(self, utterance: Utterance) -> bool:
        if utterance is None or utterance.utterance.strip() in ("", "quit", "exit"):
            self.status = SessionStatus.DISCONNECTED
            return True
        return False

    async def __call__(self):
        while True:
            # wait for user input
            user: User = yield

            # session is disconnected if a user utterance is none or empty
            if self.check_quit(user):
                return
            user.session = self
            user.parent = self.utterance
            self.utterance = user
            # agent gives all it's utterances in response to the user utterance
            async for response in agent(self.utterance):
                if self.check_quit(response):
                    return
                self.utterance = response
                # only send utterances we're asked to send
                if type(response) in self.agent_utterances:
                    yield response
            yield None


@dataclass
class VectorStoreMemory:
    utterance: Optional[Utterance] = None
    vector_store: Optional[VectorStore] = None
    default_k: int = 3


#     @property
#     def session_id(self) -> Optional[UUID]:
#         return self.utterance and self.utterance.session_id

#     async def add_memories(self, utterances: List[Utterance]):
#         for utterance in utterances:
#             if self.session_id is not None and utterance.session_id != self.session_id:
#                 raise Exception("utterances belong to the same session as this memory!")
#         if self.vector_store is None:
#             self.vector_store = VectorStore(str(self.session_id))
#         await self.vector_store.coll

#     async def search(self, query: str, k: Optional[int] = None):
#         k = k or self.default_k


@dataclass
class Agent:
    description: str
    ref_name: str
    query: Callable[["Agent", Any, ...], Coroutine[Any, Any, Utterance]]
    tools: List[Type[Tool]]
    model_identifier: str
    decoder: str = "argmax"
    memory: Optional[VectorStoreMemory] = None
    _run: Callable[[Any, ...], Coroutine[Any, Any, Utterance]] = field(default=None, init=False)
    queue: asyncio.Queue[Utterance] = field(default_factory=asyncio.Queue, init=False)

    def __post_init__(self):
        assert self.tools, "This agent requires some tools"

    async def __call__(self, session: Session) -> Utterance:
        raise NotImplementedError()

    async def asend(self, utterance: Utterance):
        await self.queue.put(utterance)
        # print(utterance)

    async def run(self, *args):
        if self._run is None:
            self._run = self._compile_query(self.query)
        return await self._run(self, *args)

    def _compile_query(self, f: Callable[["Agent", Any, ...], Coroutine[Any, Any, Utterance]]):
        assert f.__doc__, "query must have a docstring"
        sig = inspect.signature(f)
        assert [arg.name for arg in sig.parameters.values()]:2 == ["agent", 'utterance'], "First parameters to query must be `agent, utterance`"
        source = "async def _f" + str(sig) + ":\n" + ("    '''" + f.__doc__.format(**self.__dict__) + "\n    '''")
        #         print(source)
        exec(source)
        add_source(locals().get("_f"), source)
        return lmql.query(locals().get("_f"))

    async def __call__(
        self, utterances: Set[Union[Type[Observation], Type[Thought], Type[Answer]]],
    ) -> AsyncGenerator[Optional[Utterance], Utterance]:
        raise NotImplementedError()
