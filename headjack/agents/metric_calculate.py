from typing import List
import lmql
from headjack.utils import fetch
from headjack.config import get_settings
from textwrap import indent
from headjack.agents.metric_search import search_for_metrics


async def search_for_dimensions(metrics):
    settings = get_settings()
    try:
        metrics = "&".join("metric="+f.strip("\n '.") for f in metrics)
        results = await fetch(f"{settings.metric_service}/metrics/common/dimensions/?{metrics}", 'GET', return_json=True)
        return results
    except:
        return "No results"

async def calculate_metric(metrics, dimensions, filters):
    settings = get_settings()
    metrics = "&".join("metrics="+f.strip("\n '.") for f in metrics)
    dimensions = "&".join("dimensions="+f.strip("\n '.") for f in dimensions)
    filters = "&".join("filters="+f.strip("\n '.") for f in filters)
    url = f"{settings.metric_service}/data/?"
    url+=metrics
    if dimensions.strip():
        url+="&"+dimensions
    if filters.strip():
        url+="&"+filters
        
    results = await fetch(url, 'GET', return_json=True)
    return results

async def metric_calculate_agent(question: str):
    return await _metric_calculate_agent(question, [], [])

@lmql.query
async def _metric_calculate_agent(question: str, _metrics: List[str], _dimensions: List[str]):
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
        Is there a dimension that matches 'city'?: Yes, location.city.
        Is there a dimension that could be used to filter to 'month is July'?: Yes, location.month.
        Write a valid sql filter expression for 'month is July' using location.month: "location.month='July'"
        Is there a dimension that could be used to filter to 'population more than 10 million'?: Yes, location.population.
        Write a valid sql filter expression for 'population more than 10 million' using location.population: "location.population>10000000"
        # Request is run successfully and results sent to the user    
    
        User: What is the average rating and number of reviews for the top 10 highest selling products?
        Metrics Terms: 'average rating, mean rating'; 'total reviews, number of reviews';
        Metric Search Results:
            Average Rating: avg_rating
            Number of Reviews: num_reviews
            ...
        Is there a metric that appears to match 'average rating, mean rating'? Yes, avg_rating.
        Is there a metric that appears to match 'total reviews, number of reviews'? Yes, num_reviews.
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
        Is there a dimension that could be used to filter to 'top 10 highest selling products'?: No.
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
        res = await search_for_metrics(term)
        metrics = [md['name'] for md in res['metadatas'][0]]
        _metrics += metrics
        metric_texts = [f"{desc}: {m}" for desc, m in zip(res['documents'][0], metrics)]
        metric_results.append(metric_texts)
    metric_results=indent("\n".join(metric_results), " "*4)
    "Metric Search Results:\n"
    "{metric_results}"
        
    selected_metrics=[]
    for term in terms:
        "Is there a metric that appears to match '{term}'? [YESNO]"
        if YESNO=='Yes':
            ", [METRIC].\n"
            selected_metrics.append(METRIC)
        else:
            "Explain in a few words to the user why you are unable to continue with their request.\n"
            "Response: [RESULT]"
            
    common_dimensions = indent("\n".join(await search_for_dimensions(selected_metrics)), " "*4)
    if not common_dimensions:
        "There are no shared dimensions for these metrics. Explain to the user why you are unable to continue with their request.\n"
        "Response: [RESULT]"
            
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
        
    """Dimensions for {', '.join(selected_metrics)}:
    {common_dimensions}"""
    
    selected_groupbys=[]
    for term in groupbys:
        "Is there a dimension that matches '{term}'? [YESNO]"
        if YESNO=='Yes':
            ", [DIMENSION].\n"
            selected_groupbys.append(DIMENSION)
        else:
            "Explain in a few words to the user why you are unable to continue with their request.\n"
            "Response: [RESULT]"
            
    selected_filters=[]
    for term in filters:
        "Is there a dimension that could be used to filter to '{term}'? [YESNO]"
        if YESNO=='Yes':
            ", [DIMENSION].\n"
            "Write a valid sql filter expression for {term}: [FILTER]"
            selected_filters.append(FILTER)
        else:
            "Explain in a few words to the user why you are unable to continue with their request.\n"
            "Response: [RESULT]"

    return await calculate_metric(metric, dimensions, filters)
    
from
    "chatgpt"
where
    STOPS_AT(TERM, "'") and
    STOPS_AT(RESULT, "\n") and
    STOPS_AT(FILTER, "\n") and
    YESNO in ['Yes', 'No'] and
    METRIC in _metrics and
    DIMENSION in _dimensions
    '''