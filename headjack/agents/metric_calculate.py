from typing import List
import lmql
from headjack.utils import fetch
from headjack.config import get_settings
from textwrap import indent
from headjack.tools.metric_search import metric_search

async def calculate_metric(metric, dimensions, filters):
    settings = get_settings()
    filters = [f.strip("\n '.") for f in filters]
    # TODO: Use metric, dimensions, and filters to calculate the desired result
    #       and return it as a string
    return "Result"

@lmql.query
async def metric_calculate_agent(question: str, _dimensions: List[str]):
    '''lmql
argmax
    """You are given a User request to calculate a metric using a tool. 
    From the User request you will need to deduce the following information:
    A. What metric(s) is the user requesting?
        1. To do this you must first identify what terms to do a metric search for to bring back possible metrics.
        2. Decide whether there are any metrics you should use based on the results.
    B. What dimensions the user is requesting?
        1. Are there any dimensions in the user's request wanting to group by a dimension or filter by it and which.
        1. If you have decided that there is a valid metric, you must then search for the dimensions that can be used. A search will be performed using your chosen metric and you will be shown the possible dimensions.
        2. Which, if any, of the dimensions are appropriate for grouping and filtering.
    C. With this information either a request for the data will be directly returned to the user, or if the user's request cannot be fullfilled, an explanation to the user returned.
    
    Here are some examples:
        User: What is the average temperature by city for the month of July where the city's population is more than 10 million?
        Metrics Terms: 'average temperature, mean temperature';
        Metric Search Results:
            Average Temperature: avg_temp
            Minimum Temperature: min_temp
            ...
        Is there a metric that appears to match 'average temperature, mean temperature'? Yes, avg_temp.
        Group By: 'city, town, municipality';
        Filter By: 'month is July'; 'population more than 10 million';
        Dimensions for avg_temp:
            location.population
            location.city
            location.month
            location.state
            ...
        Are there any dimensions that match 'city'?: Yes, location.city.
        Are there any dimensions that could be used to filter to 'month is July'?: Yes, location.month.
        Are there any dimensions that could be used to filter to 'population more than 10 million'?: Yes, location.population.
        Write a valid sql filter expression for 'month is July' using location.month: "location.month='July'"
        Write a valid sql filter expression for 'population more than 10 million' using location.population: "location.population>10000000"
        # Request is run successfully and results sent to the user    
    
        User: What is the average rating and number of reviews for the top 10 highest selling products?
        Metrics Terms: 'average rating, mean rating'; 'total reviews, number of reviews';
        Metric Search Results:
            Average Rating: avg_rating
            Number of Reviews: num_reviews
            ...
        Is there a metric that appears to match the User's request? Yes, there are two metrics: avg_rating and num_reviews.
        Group By:
        Filter By: 'top 10 highest selling products';
        Dimensions for avg_rating, num_reviews:
            item.name
            item.category
            item.id
            ...
            store.name
            store.id
            store.location
        Are there any dimensions that could be used to filter to 'top 10 highest selling products'?: No.
        Response: The requested metric data could not be calculated because there is no dimension that can be used to filter to the top 10 highest selling products.
        # Response sent to user
    
    
    User: {question}
    Metrics Terms: """
    terms=[]
    for i in range(5):
        if terms and terms[-1].endswith('\n'):
            break
        "'[TERM];"
        terms.append(TERM.strip("\n '."))
        
    metric_results = []
    for term in terms:
        res = await metric_search(term)
        metrics = [f"{desc}: {md['name']}" for desc, md in zip(res['documents'][0], res['metadatas'][0])]
        metric_results.append(metrics)
    metric_results=indent("\n".join(metric_results), " "*4)
    "Metric Search Results:\n"
    "{metric_results}"
        
    for term in terms:
        "Is there a metric that appears to match '{term}'? Yes, avg_temp."
    "Group By: "
    groupbys=[]
    for i in range(5):
        if groupbys and groupbys[-1].endswith('\n'):
            break
        "'[GROUPBY];"
        groupbys.append(GROUPBY)
        
    "Filter By: "
    filters=[]
    for i in range(5):
        if filters and filters[-1].endswith('\n'):
            break
        "'[FILTER];"
        filters.append(FILTER)
        
    
    


    # TODO: Use the dimensions and filters to calculate the desired result
    result = await calculate_metric(metric, dimensions, filters)
    

from
    "chatgpt"
where
    STOPS_AT(TERM, "'") and YESNO in ['Yes', 'No']
    '''