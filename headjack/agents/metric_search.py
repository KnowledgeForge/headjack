import lmql
from headjack.utils import fetch
from headjack.config import get_settings

async def search_for_metrics(q):
    settings = get_settings()
    try:
        q = q.strip("\n '.")
        results = await fetch(f"{settings.search_service}/query?collection=metrics&text={q}", 'GET', return_json=True)
        return [i for j in results['documents'] for i in j]
    except:
        return "No results"

@lmql.query
async def metric_search_agent(question: str):
    '''
argmax
    """You are given some statement, terms or question below from the User.
    
    Here are some examples:
    User: "What is the average temperature by city for the month of July?"
    Terms: "average temperature", "mean temperature"

    User: "total sales by region for the quarter ending September 2023?"
    Terms: "total sales", "sales", "revenue"
    
    User: "What is the total revenue for the company for the year 2022?"
    Terms: "total revenue", "revenue", "sales"
    
    User: "What is the average number of employees by department?"
    Terms: "average number of employees", "mean number of employees"
    
    User:"What is the total number of flights by airline for the month of October?"
    Terms: "total number of flights", "number of flights"

    User: "avg rating for the restaurant by cuisine type"
    Terms: "average rating", "mean rating"
    
    User: "registered users"
    Terms: "total users", "number of users", "registered users"
    
    """
    "Question: {question}\n"
    "Action: Let's search for the terms '[TERM]\n"
    result = await search_for_metrics(TERM)
    "Result: {result}\n"
    "Final Answer:[ANSWER]"
FROM 
    "chatgpt"
WHERE
    STOPS_AT(TERM, "'")
    '''