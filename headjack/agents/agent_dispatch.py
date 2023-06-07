import logging
from dataclasses import dataclass
from textwrap import dedent, indent  # noqa: F401
from typing import List

import lmql

from headjack.agents.registry import AGENT_REGISTRY
from headjack.models.utterance import Utterance
from headjack.utils.consistency import consolidate_responses

_logger = logging.getLogger("uvicorn")


dispatchable_agents = indent(
    dedent("\n".join([f"{agent_name}: {agent_description}" for agent_name, (agent_description, _) in AGENT_REGISTRY.items()])),
    " " * 4,
)


async def agent_dispatch(question: Utterance, n: int = 1, temp: float = 0.0) -> Utterance:
    return await consolidate_responses(await _agent_dispatch(AgentDispatchArgs(question, n, temp)))


@dataclass
class AgentDispatchArgs:
    question: Utterance
    n: int
    temp: float


@lmql.query
async def _agent_dispatch(args: AgentDispatchArgs) -> List[Utterance]:  # type: ignore
    '''lmql
    argmax
        """You are an agent that interprets a user request and determines what specialist is best suited to handle the request.

        The specialists at your disposal to dispatch to are:
            {dispatchable_agents}

        User: {args.question.utterance}
        The agent that seems best suited to handle this request is: [AGENT]
        """
        _logger.info(f"Dispatching to {AGENT} for user request `{args.question}`.")
        return await AGENT_REGISTRY[AGENT][1](args.question, args.n, args.temp)

    from
        "chatgpt"
    where
        AGENT in [agent for agent in AGENT_REGISTRY.keys()]
    '''
