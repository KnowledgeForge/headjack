import logging
from typing import Union

import lmql
from lmql.runtime.bopenai import get_stats

from headjack.agents.registry import register_agent_function
from headjack.config import get_settings
from headjack.models.utterance import Answer, Response, Utterance
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.basic import list_dedup, strip_whole  # noqa: F401
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
    ret = await consolidate_responses(add_source_to_utterances(await _messages_search_agent(question, n, temp), "messages_search_agent"))  # type: ignore
    _logger.info(get_stats())
    return ret


@lmql.query
async def _messages_search_agent(question: Utterance, n: int, temp: float) -> Union[Response, Answer]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp)
        "Given the following question, use a term to search for relevant conversations in the messaging system and create a summary answer. "
        "Try to find the names of the people in the conversation and include their names in the summary. Use quotes of the messages as examples "
        "of key points in your summary. If there's a clear sentiment across the conversations returned by the messaging system, make sure to include "
        "that in your answer.\n"
        "Question: {question.utterance}\n"
        "In just a few words on a single line, explain what the Question is asking: [EXPLAIN]"
        "\nCreate several diverse queries that are likely to bring back messages likely to be relevant based on the Question/Topic."
        tasks = []
        for i in range(3):
            "Query: '[TERM]\n"
            task = asyncio.create_task(search_for_messages(TERM))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        results = list_dedup([doc for res in results for doc in res if res != 'No results'])
        str_results = [str(doc) for doc in results]

        if not results:
            return Response(utterance="There were no people found for `{question.utterance}`.", parent = question)

        knowledge = "\n\n".join(str_results)
        """Here are some potentially relevenant messages from the message system:

        {knowledge}

        Some or all of these may be irrelvant towards replying to `{question.utterance}`.
        If there are not relevant messages, summarize what you found, but explain why you believe it is not relevant.
        Summarize and explain all the information you found.
        Answer:[ANSWER]"""
        "In participants tags, generate a comma-separated list of the names of all participants explicitly or implicitly taking part in the conversation like `<participants>person 1, person 2,...</participants>`: \n"
        "<participants>[PARTICIPANTS]participants>"
        participants=[ptcp.strip() for ptcp in strip_whole(PARTICIPANTS, "</").split(",")]
        return Answer(utterance=ANSWER, metadata={"participants": participants}, parent = question)
    FROM
        "chatgpt"
    WHERE
        STOPS_AT(TERM, "'") and
        STOPS_AT(PARTICIPANTS, "</")
    '''
