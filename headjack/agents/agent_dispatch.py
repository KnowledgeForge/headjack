import logging
from textwrap import dedent, indent  # noqa: F401

import lmql

from headjack.agents.registry import AGENT_REGISTRY
from headjack.models.utterance import Utterance

_logger = logging.getLogger("uvicorn")


dispatchable_agents = indent(
    dedent("\n".join([f"{agent_name}: {agent_description}" for agent_name, (agent_description, _) in AGENT_REGISTRY.items()])),
    " " * 4,
)


@lmql.query
async def agent_dispatch(question: Utterance) -> Utterance:  # type: ignore
    '''lmql
    argmax
        """You are an agent that interprets a user request and determines what specialist is best suited to handle the request.

        The specialists at your disposal to dispatch to are:
            {dispatchable_agents}

        User: {question.utterance}
        The agent that seems best suited to handle this request is: [AGENT]
        """
        _logger.info(f"Dispatching to {AGENT} for user request `{question}`.")
        return await AGENT_REGISTRY[AGENT][1](question)

    from
        "chatgpt"
    where
        AGENT in [agent for agent in AGENT_REGISTRY.keys()]
    '''
