import asyncio
import inspect
from dataclasses import dataclass, field
from textwrap import dedent
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Type,
    cast,
)

import lmql

from headjack.utils.general import add_source

if TYPE_CHECKING:
    # from headjack.models.memory import VectorStoreMemory
    from headjack.models.tool import Tool
    from headjack.models.utterance import User, Utterance


@dataclass
class Agent:
    description: str
    ref_name: str
    query: Callable[["Agent", "Utterance", Any], Coroutine[Any, Any, "Utterance"]]
    tools: List[Type["Tool"]]
    model_identifier: str
    decoder: str = "argmax"
    # memory: Optional["VectorStoreMemory"] = None
    _run: Optional[Callable[["Agent", "Utterance", Any], Coroutine[Any, Any, "Utterance"]]] = field(default=None, init=False)
    queue: asyncio.Queue["Utterance"] = field(default_factory=asyncio.Queue, init=False)

    def __post_init__(self):
        if not self.tools:
            raise Exception("This agent requires some tools")
        # for tool in self.tools:
        #     queries, name = tool.schema.examples.keys(), tool.name
        #     self.tool_example_lookup.add(queries, [{'idx': i} for i in range(len(queries))], [name]*len(queries))

        # import pdb; pdb.set_trace()

    async def asend(self, utterance: "Utterance"):
        print(utterance)
        await self.queue.put(utterance)

    async def run(self, *args):
        if self._run is None:
            self._run = self._compile_query(self.query)
        return await self._run(self, *args)

    def _compile_query(self, f: Callable[["Agent", "Utterance", Any], Coroutine[Any, Any, "Utterance"]]):
        assert f.__doc__, "query must have a docstring"
        doc = dedent(f.__doc__)
        sig = inspect.signature(f)
        arg_names = tuple([arg.name for arg in sig.parameters.values()])
        assert arg_names[:2] == ("agent", "utterance"), "First parameters to query must be `agent, utterance`"

        source = "async def _f(" + ", ".join(arg_names) + "):\n" + ("    '''" + doc.format(**self.__dict__) + "\n    '''")
        #         print(source)
        from headjack.models.tool import Tool, dyn_filter  # noqa: disable=F401
        from headjack.models.utterance import (  # noqa: disable=F401
            Action,
            Answer,
            Feedback,
            Observation,
            Thought,
            User,
            Utterance,
        )

        dynamic_filter: Dict[Any, Any] = {}  # noqa: disable=F401
        exec(source, globals(), locals())
        print(source)
        assert locals().get("_f") is not None, "failed to compile query"
        add_source(cast(Callable, locals().get("_f")), source)
        return lmql.query(cast(Callable, locals().get("_f")))

    async def __call__(self, user: "User") -> AsyncGenerator[Optional["Utterance"], "Utterance"]:
        raise NotImplementedError()
