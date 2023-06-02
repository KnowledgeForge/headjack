import logging
from textwrap import dedent, indent  # noqa: F401
from typing import Any, List, Set

import lmql

from headjack.agents.registry import AGENT_REGISTRY
from headjack.config import get_settings
from headjack.utils import fetch
from headjack.utils.semantic_sort import semantic_sort  # noqa: F401

_logger = logging.getLogger("uvicorn")


dispatchable_agents = indent(dedent("\n".join([f"{agent_name}: {agent_description}" for agent_name, (agent_description, _) in AGENT_REGISTRY.items()])), " "*4)

@lmql.query
async def agent_dispatch(question: str)-> Any:
    '''lmql
    argmax
        """You are an agent that interprets a user request and determines what specialist is best suited to handle the request.
        
        The specialists at your disposal to dispatch to are:
            {dispatchable_agents}

        User: {question}
        The agent that seems best suited to handle this request is: [AGENT]
        """
        _logger.info(f"Dispatching to {AGENT} for user request `{question}`.")
        return await AGENT_REGISTRY[AGENT][1](question)

    from
        "chatgpt"
    where
        AGENT in list(AGENT_REGISTRY.keys())
    '''
