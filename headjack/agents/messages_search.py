import logging
from typing import Union

import lmql

from headjack.agents.registry import register_agent_function
from headjack.config import get_settings
from headjack.models.utterance import Answer, Response, Utterance
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.consistency import consolidate_responses

_logger = logging.getLogger("uvicorn")


async def search_for_messages(q):
    settings = get_settings()
    try:
        q = q.strip("\n '.")
        _logger.info("Searching messages collection using the headjack search service")
        results = await fetch(f"{settings.search_service}/query?collection=messages&text={q}", "GET", return_json=True)
        return [i for j in results["documents"] for i in j]
    except Exception as e:
        _logger.info(f"Error while attempting to reach headjack search service messages collection: {str(e)}")
        return "No results"


@register_agent_function(
    "This is a search over a messaging system. Provided a query, this will give a summary of conversations found in the messaging system.",
)
async def messages_search_agent(question: Utterance, n: int = 1, temp: float = 0.0) -> Union[Response, Answer]:
    return await consolidate_responses(add_source_to_utterances(await _messages_search_agent(question, n, temp), "messages_search_agent"))  # type: ignore


@lmql.query
async def _messages_search_agent(question: Utterance, n: int, temp: float) -> Union[Response, Answer]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp)
        "Given the following question, use a term to search for relevant conversations in the messaging system and create a summary answer. "
        "Try to find the names of the people in the conversation and include their names in the summary. Use quotes of the messages as examples "
        "of key points in your summary. If there's a clear sentiment across the conversations returned by the messaging system, make sure to include "
        "that in your answer.\n"
        "Question: {question.utterance}\n"
        "Action: Let's search for the term '[TERM]\n"
        result = await search_for_messages(TERM)
        if result == 'No results':
            return Response(utterance=result, parent_ = question)
        "Result: {result}\n"
        "Final Answer:[ANSWER]"
        return Answer(utterance=ANSWER, parent_ = question)
    FROM
        "chatgpt"
    WHERE
        STOPS_AT(TERM, "'")
    '''
