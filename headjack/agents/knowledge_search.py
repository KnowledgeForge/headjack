import lmql
from headjack.utils import fetch

async def search_for_knowledge(q):
   try:
      q = q.strip("\n '.")
      results = await fetch(f"http://0.0.0.0:16410/query?collection=knowledge&text={q}", 'GET', return_json=True)
      return [i for j in results['documents'] for i in j]
   except:
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