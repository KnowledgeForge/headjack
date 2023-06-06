import logging
from typing import Union

import lmql

from headjack.agents.registry import register_agent_function
from headjack.config import get_settings
from headjack.models.utterance import (  # noqa: F401
    Answer,
    Observation,
    Response,
    Utterance,
)
from headjack.utils import fetch

_logger = logging.getLogger("uvicorn")


async def search_for_metrics(q, n: int = 5):
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
    """This function takes a query to search for some metric which is a value that can be calculated such as average, total, etc.""",
)
async def metric_search_agent(question: Utterance, n: int = 1, temp: float = 0.0) -> Union[Answer, Response]:
    return await _metric_search_agent(question, n, temp)


@lmql.query
async def _metric_search_agent(question: Utterance, n: int, temp: float) -> Union[Answer, Response]:  # type: ignore
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
            return Response(utterance=result, parent_=question)
        return Observation(utterance=result, parent_=question)
    FROM
        "chatgpt"
    WHERE
        STOPS_AT(TERM, "'")
    '''
