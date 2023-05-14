import lmql
import logging
from headjack.utils import fetch
from headjack.config import get_settings

_logger = logging.getLogger("uvicorn")

async def search_for_knowledge(q):
    settings = get_settings()
    try:
        q = q.strip("\n '.")
        _logger.info(
            "Searching knowledge collection using the headjack search service"
        )
        results = await fetch(f"{settings.search_service}/query?collection=knowledge&text={q}", 'GET', return_json=True)
        return [i for j in results['documents'] for i in j]
    except Exception as e:
        _logger.info(
            "Error while attempting to reach headjack search "
            f"service knowledge collection: {str(e)}"
        )
        return "No results"

@lmql.query
async def knowledge_search_agent(question: str):
    '''
argmax
    "Given the following question, use a term to search for relevant information and create a summary answer.\n"
    "Question: {question}\n"
    "Action: Let's search for the term '[TERM]\n"
    result = await search_for_knowledge(TERM)
    "Result: {result}\n"
    "Final Answer:[ANSWER]"
FROM 
    "chatgpt"
WHERE
    STOPS_AT(TERM, "'")
    '''