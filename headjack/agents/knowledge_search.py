import logging
from typing import Union

import lmql
from lmql.runtime.bopenai import get_stats

from headjack.agents.registry import register_agent_function
from headjack.config import get_settings
from headjack.models.utterance import Answer, Response, Utterance
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.basic import list_dedup  # noqa: F401
from headjack.utils.consistency import consolidate_responses

_logger = logging.getLogger("uvicorn")


async def search_for_knowledge(q):
    settings = get_settings()
    try:
        q = q.strip("\n '.")
        _logger.info("Searching knowledge collection using the headjack search service")
        results = await fetch(f"{settings.search_service}/query?collection=knowledge&text={q}", "GET", return_json=True)
        return [i for j in results["documents"] for i in j]
    except Exception as e:
        _logger.info("Error while attempting to reach headjack search " f"service knowledge collection: {str(e)}")
        return "No results"


@register_agent_function(
    "This is a general knowledge search. Provided a query, this will give a summary of information but CANNOT help you answer questions about you or the current conversation.",
)
async def knowledge_search_agent(question: Utterance, n: int = 1, temp: float = 0.0) -> Union[Response, Answer]:
    ret = await consolidate_responses(add_source_to_utterances(await _knowledge_search_agent(question, n, temp), "knowledge_search_agent"))  # type: ignore
    _logger.info(get_stats())
    return ret


@lmql.query
async def _knowledge_search_agent(question: Utterance, n: int, temp: float) -> Union[Response, Answer]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp)
        "Given the following question, use several diverse search queries to search for relevant information and create a summary answer.\n"
        "Question: {question.utterance}\n"
        "In just a few words on a single line, explain what the Question is asking: [EXPLAIN]"
        "\nCreate several diverse queries that are likely to bring back documents likely to contain relevant information to respond to the Question."
        tasks = []
        for i in range(3):
            "Query: '[TERM]\n"
            task = asyncio.create_task(search_for_knowledge(TERM))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        results = list_dedup([doc for res in results for doc in res if res != 'No results'])

        if not results:
            return Response(utterance="There were no relevant knowledge documents found or there is an issue with the knowledge service.", parent = question)
        knowledge = indent(dedent("\n\n".join(results)), " "*4)
        """Here is the information from searching based on your queries.

        {knowledge}

        Some or all of this information may be irrelvant towards answering the question `{question.utterance}`. Do your best to determine whether the information is relevant.
        If there is not relevant information, summarize what you found but explain why you believe it is not relevant.
        Answer:[ANSWER]"""
        return Answer(utterance=ANSWER, parent = question)
    FROM
        "chatgpt"
    WHERE
        STOPS_AT(TERM, "'") and
        STOPS_AT(EXPLAIN, "\n")
    '''
