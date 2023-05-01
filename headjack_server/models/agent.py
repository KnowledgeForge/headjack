import asyncio
import inspect
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Coroutine, List, Optional, Type, cast

import lmql

from headjack_server.utils import add_source

if TYPE_CHECKING:
    from headjack_server.models.memory import VectorStoreMemory
    from headjack_server.models.tool import Tool
    from headjack_server.models.utterance import User, Utterance


@dataclass
class Agent:
    description: str
    ref_name: str
    query: Callable[["Agent", "Utterance", Any], Coroutine[Any, Any, "Utterance"]]
    tools: List[Type["Tool"]]
    model_identifier: str
    decoder: str = "argmax"
    memory: Optional["VectorStoreMemory"] = None
    _run: Optional[Callable[["Agent", "Utterance", Any], Coroutine[Any, Any, "Utterance"]]] = field(default=None, init=False)
    queue: asyncio.Queue["Utterance"] = field(default_factory=asyncio.Queue, init=False)

    def __post_init__(self):
        assert self.tools, "This agent requires some tools"

    async def asend(self, utterance: "Utterance"):
        await self.queue.put(utterance)
        # print(utterance)

    async def run(self, *args):
        if self._run is None:
            self._run = self._compile_query(self.query)
        return await self._run(self, *args)

    def _compile_query(self, f: Callable[["Agent", "Utterance", Any], Coroutine[Any, Any, "Utterance"]]):
        assert f.__doc__, "query must have a docstring"
        sig = inspect.signature(f)
        arg_names = tuple([arg.name for arg in sig.parameters.values()])
        assert arg_names[:2] == ("agent", "utterance"), "First parameters to query must be `agent, utterance`"

        source = "async def _f(" + ", ".join(arg_names) + "):\n" + ("    '''" + f.__doc__.format(**self.__dict__) + "\n    '''")
        #         print(source)
        from headjack_server.models.utterance import Action, Answer, Observation, Thought, User, Utterance  # noqa: F401

        exec(source, globals(), locals())
        assert locals().get("_f") is not None, "failed to compile query"
        add_source(cast(Callable, locals().get("_f")), source)
        return lmql.query(cast(Callable, locals().get("_f")))

    async def __call__(self, user: "User") -> AsyncGenerator[Optional["Utterance"], "Utterance"]:
        raise NotImplementedError()