import asyncio  # noqa: F401
import logging
from typing import Union

import lmql
from lmql.runtime.bopenai import get_stats

from headjack.agents.registry import register_agent_function
from headjack.config import get_settings
from headjack.models.utterance import Answer, Observation, Response, Utterance
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.basic import list_dedup  # noqa: F401
from headjack.utils.consistency import consolidate_responses

_logger = logging.getLogger("uvicorn")


async def search_for_people(q, n: int = 5):
    settings = get_settings()
    try:
        q = q.strip("\n '.")
        _logger.info("Searching people collection using the headjack search service")
        results = await fetch(f"{settings.search_service}/query?collection=people&n={n}&text={q}", "GET", return_json=True)
        metadata = results["metadatas"][0]
        for i, m in enumerate(metadata):
            m["description"] = results["documents"][0][i]
        return metadata
    except Exception as e:
        _logger.info(f"Error while attempting to reach headjack search service people collection: {str(e)}")
        return "No results"


@register_agent_function(
    "This is a search over a human resources system with information on people within the organization. "
    "Provided a query, this will give a summary of conversations found in the messaging system.",
)
async def people_search_agent(question: Utterance, n: int = 1, temp: float = 0.0) -> Union[Response, Answer]:
    ret = await consolidate_responses(add_source_to_utterances(await _people_search_agent(question, n, temp), "people_search_agent"))  # type: ignore
    _logger.info(get_stats())
    return ret


@lmql.query
async def _people_search_agent(question: Utterance, n: int, temp: float) -> Union[Response, Observation]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp)
        "Given the following question or topic, use a comma-separated set of terms to search for people in the human resource system and create a list of people. "
        "Use terms that would be found in a the job description and/or bio of the person in the human resource system. That will help you find people "
        "that are most likely right people to reach out to in order to answer the question or learn more about the topic."
        "\n"
        "Question/Topic: {question.utterance}\n"
        "In just a few words on a single line, explain what the Question is asking: [EXPLAIN]"
        "\nCreate several diverse queries that are likely to bring back people likely to be relevant based on the Question/Topic."
        tasks = []
        for i in range(3):
            "Query: '[TERM]\n"
            task = asyncio.create_task(search_for_people(TERM))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        results = list_dedup([doc for res in results for doc in res if res != 'No results'])
        str_results = [str(doc) for doc in results]

        if not results:
            return Response(utterance="There were no people found for `{question.utterance}`.", parent = question)

        knowledge = "\n\n".join(str_results)
        """Here is the information from searching based on your queries.

        {knowledge}

        Some or all of these may be irrelvant towards replying to `{question.utterance}`.
        If there are not relevant people, summarize what you found, but explain why you believe it is not relevant.
        Summarize and explain all the information you found to the user including any recommendations on which people are most relevant to the Question/Topic.
        Answer:[ANSWER]"""

        return Answer(utterance=ANSWER, metadata = {"people": results}, parent = question)
    FROM
        "chatgpt"
    WHERE
        STOPS_AT(TERM, "\n") and
        STOPS_AT(EXPLAIN, "\n")
    '''
