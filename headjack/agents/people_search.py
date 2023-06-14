import logging
from typing import Union

import lmql

from headjack.agents.registry import register_agent_function
from headjack.config import get_settings
from headjack.models.utterance import Answer, Response, Observation, Utterance
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.consistency import consolidate_responses

_logger = logging.getLogger("uvicorn")


async def search_for_people(q):
    settings = get_settings()
    try:
        q = q.strip("\n '.")
        _logger.info("Searching people collection using the headjack search service")
        results = await fetch(f"{settings.search_service}/query?collection=people&n=4&text={q}", "GET", return_json=True)
        metadata = results["metadatas"][0]
        for i, m in enumerate(metadata):
            m["description"] = results["documents"][0][i]
        return metadata
    except Exception as e:
        _logger.info(f"Error while attempting to reach headjack search service people collection: {str(e)}")
        return "No results"


@register_agent_function(
    "This is a search over a human resources system with information on people within the organization."
    "Provided a query, this will give a summary of conversations found in the messaging system.",
)
async def people_search_agent(question: Utterance, n: int = 1, temp: float = 0.0) -> Union[Response, Answer]:
    return await consolidate_responses(add_source_to_utterances(await _people_search_agent(question, n, temp), "people_search_agent"))  # type: ignore


@lmql.query
async def _people_search_agent(question: Utterance, n: int, temp: float) -> Union[Response, Observation]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp)
        "Given the following question or topic, use a term to search for people in the human resource system and create a list of people. "
        "Use terms that would be found in a the job description of the person in the human resource system. That will help you find the people "
        "that are most likely the right person to reach out to in order to answer the question or learn more about the topic."
        "\n"
        "Question/Topic: {question.utterance}\n"
        "Action: Let's search for the term '[TERM]\n"
        result = await search_for_people(TERM)
        if result == 'No results':
            return Response(utterance=result, parent_ = question)
        "Result: {result}\n"
        "Final Answer:[ANSWER]\n"
        return Observation(utterance={"summary": ANSWER, "people": result}, parent_ = question)
    FROM
        "chatgpt"
    WHERE
        STOPS_AT(TERM, "'")
    '''
