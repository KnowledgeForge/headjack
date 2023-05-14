import lmql
from headjack.utils import fetch
from headjack.config import get_settings

async def search_for_metrics(q):
    settings = get_settings()
    try:
        q = q.strip("\n '.")
        results = await fetch(f"{settings.search_service}/query?collection=metrics&text={q}", 'GET', return_json=True)
        return results
    except:
        return "No results"

@lmql.query
async def metric_search_agent(question: str):
    '''
argmax
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
    "User: {question}\n"
    "Terms: '[TERM]\n"
    return await search_for_metrics(TERM)
FROM 
    "chatgpt"
WHERE
    STOPS_AT(TERM, "'")
    ''