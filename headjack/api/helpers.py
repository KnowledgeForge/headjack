from headjack.tools.knowledge_search import knowledge_search  # isort:skip
from headjack.tools.metric_search import metric_search  # isort:skip
from headjack.tools.metric_dimension_search import metric_dimension_search  # isort:skip  # noqa: F401
from headjack.tools.metric_calculate import metric_calculate  # isort:skip

from typing import Any, Dict
from uuid import UUID, uuid4

import jwt

from headjack.config import get_headjack_secret
from headjack.models.session import Session


def decode_token(access_token: str) -> Dict[str, Any]:
    return jwt.decode(access_token, get_headjack_secret(), algorithms=["HS256"])


def get_agent_session(access_token: str):
    payload = decode_token(access_token)
    session_id = payload["session_id"]
    session_uuid = UUID(session_id)
    if session := Session.sessions.get(session_uuid):
        return session
    from headjack.agents.standard import StandardAgent

    tools = [knowledge_search, metric_search, metric_calculate]
    agent = StandardAgent(
        model_identifier="chatgpt",
        # model_identifier="openai/text-davinci-003",
        tools=tools,
        decoder="argmax(openai_chunksize=4, chatty_openai=True)",
    )
    session = Session(agent, session_id=session_uuid)
    return session


def get_access_token():
    return jwt.encode({"session_id": str(uuid4())}, get_headjack_secret(), algorithm="HS256")
