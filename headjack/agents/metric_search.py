import logging
from typing import Union

import lmql
from lmql.runtime.bopenai import get_stats

from headjack.agents.registry import register_agent_function
from headjack.config import get_settings
from headjack.models.utterance import (  # noqa: F401
    Answer,
    Observation,
    Response,
    Utterance,
)
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.consistency import consolidate_responses

_logger = logging.getLogger("uvicorn")


async def search_for_metrics(q, n: int = 15):
    settings = get_settings()
    try:
        q = q.strip("\n '.")
        _logger.info(f"Searching metrics collection using the headjack search service: `{q}`")
        results = await fetch(f"{settings.search_service}/query?collection=metrics&text={q}&n={n}", "GET", return_json=True)
        return results
    except Exception as e:
        _logger.info("Error while attempting to reach the headjack " f"search service metrics collection: {str(e)}")
        return "No results"


@register_agent_function(
    """This agent takes a query to search for some metric which DEFINES something like an average, total, etc. over some data.
    This is NOT an agent for calculation nor is it needed before running a calculation. It is used only for discovering metrics.
    This agent needs a specific metric or topic to work best i.e. NOT "find some metrics".""",
)
async def metric_search_agent(
    question: Utterance,
    n: int = 1,
    temp: float = 0.0,
    chat_context: bool = False,
) -> Union[Answer, Response]:
    ret = await consolidate_responses(add_source_to_utterances(await _metric_search_agent(question, n, temp, chat_context), "metric_search_agent"))  # type: ignore
    _logger.info(get_stats())
    return ret


@lmql.query
async def _metric_search_agent(question: Utterance, n: int, temp: float, chat_context: bool) -> Union[Answer, Response]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp)
        """You are given some statement, terms or question below from the User.
        You will generate a list of diverse potential search terms that will be searched.

        Here are some examples:
        User: What is the average temperature by city for the month of July?
        Terms: 'average temperature, mean temperature'

        User: total sales by region for the quarter ending September 2023
        Terms: 'total sales, sales, revenue'

        User: avg rating for the restaurant by cuisine type
        Terms: 'average rating, mean rating'

        User: registered users
        Terms: 'total users, number of users, registered users'

        """
        "User: {question.utterance}\n"
        "Terms: '[TERM]\n"
        result = await search_for_metrics(TERM)
        if result=='No results':
            return Response(utterance="There were no metrics found for `{question.utterance}`.", parent=question)
        response = "Metric Search completed for `{question.utterance}`."
        if chat_context:
            "The search has been completed. Here are the results:\n"
            {result}
            "Summarize the resuls and explain in a few words all that you have done to complete this request.\n"
            "[RESPONSE]"
            response = RESPONSE
        return Observation(utterance=response, metadata=result, parent=question)
        "{chat_context}"
    FROM
        "chatgpt"
    WHERE
        STOPS_AT(TERM, "'")
    '''
