from typing import List
import lmql
import logging
from headjack.utils import fetch
from headjack.config import get_settings
from textwrap import indent
from headjack.agents.metric_search import search_for_metrics

_logger = logging.getLogger("uvicorn")

async def search_for_dimensions(metrics):
    settings = get_settings()
    try:
        metrics = "&".join("metric="+f.strip("\n '.") for f in metrics)
        _logger.info(
            "Searching for dimensions using the metrics service"
        )
        results = await fetch(f"{settings.metric_service}/metrics/common/dimensions/?{metrics}", 'GET', return_json=True)
        return results
    except Exception as e:
        _logger.info(
            f"Error while attempting to reach the metric service {str(e)}"
        )
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
    
    try:
        _logger.info(
            f"Calculating metric using the metrics service"
        )
        results = await fetch(url, 'GET', return_json=True)
    except Exception as e:
        _logger.info(
            f"Error while attempting to reach metrics service {str(e)}"
        )
        return "Cannot calculate metric"
    return results

async def metric_calculate_agent(question: str):
    return await _metric_calculate_agent(question, [], [])

@lmql.query
async def _metric_calculate_agent(question: str, _metrics: List[str], _dimensions: List[str]):
    '''lmql
argmax
    """You are given a User request to calculate a metric using a tool. 

    Here are some examples:
        User: What is the average temperature by city for the month of July where the city's population is more than 10 million?
        Thought: There's 1 metric(s) being requested, 1 group by dimension(s) being requested, and 2 filter dimension(s) being requested.
        <Metrics Terms>
        average temperature mean temperature
        </Metrics Terms>
        <Metric Search Results>
        Average Temperature: avg_temp
        Minimum Temperature: min_temp
        ...
        </Metric Search Results>
        Is there a metric that appears to match 'average temperature mean temperature'? Yes, avg_temp.
        <Group By>
         city, town, municipality
        </Group By>
        <Filter By>
        month is July
        population more than 10 million
        </Filter By>
        <Dimensions metrics=avg_temp>
            location.population
            location.city
            location.month
            location.state
            ...
        </Dimensions>
        Is there a dimension that matches 'city'?: Yes, location.city.
        Is there a dimension that could be used to filter to 'month is July'?: Yes, location.month.
        Write a valid sql filter expression for 'month is July' using location.month: 
        <sql filter expression>location.month='July'</sql filter expression>
        Is there a dimension that could be used to filter to 'population more than 10 million'?: Yes, location.population.
        Write a valid sql filter expression for 'population more than 10 million' using location.population: 
        <sql filter expression>location.population>10000000</sql filter expression>
        # Request is run successfully and results sent to the user    

        User: What is the average rating and number of reviews for the top 10 highest selling products?
        Thought: There's 2 metric(s) being requested, 0 group by dimension(s) being requested, and 1 filter dimension(s) being requested.
        <Metrics Terms>
        average rating mean rating
        total reviews, number of reviews
        </Metrics Terms>
        <Metric Search Results>
        Average Rating: avg_rating
        Number of Reviews: num_reviews
        ...
        </Metric Search Results>
        Is there a metric that appears to match 'average rating mean rating'? Yes, avg_rating.
        Is there a metric that appears to match 'total reviews number of reviews'? Yes, num_reviews.
        <Group By>
        </Group By>
        <Filter By>
        top 10 highest selling products
        </Filter By>
        <Dimensions metrics=avg_rating, num_reviews>
        item.name
        item.category
        item.id
        ...
        store.name
        store.id
        store.location
        </Dimensions>
        Is there a dimension that could be used to filter to 'top 10 highest selling products'?: No.
        Response: The requested metric data could not be calculated because there is no dimension that can be used to filter to the top 10 highest selling products.
        # Response sent to user
    
    
    User: {question}
    Thought: There's [METRIC_COUNT] metric(s) being requested, [GROUPBY_COUNT] group by dimension(s) being requested, and [FILTER_COUNT] filter dimension(s) being requested.
    <Metric Terms>
    """
    terms=[]
    for i in range(int(METRIC_COUNT)):
        "[METRIC_TERM]"
        terms.append(METRIC_TERM.strip("\n '."))
    "</Metric Terms>\n"
    metric_results = []
    for term in terms:
        res = await search_for_metrics(term)
        metrics = [md['name'] for md in res['metadatas'][0]]
        _metrics += metrics
        metric_texts = [f"{desc}: {m}" for desc, m in zip(res['documents'][0], metrics)]
        metric_results+=metric_texts
    metric_results="\n".join(metric_results)

    "<Metric Results>\n"
    "{metric_results}"
    "\n</Metric Results>\n"
    
    selected_metrics=[]
    for term in terms:
        "Is there a metric that appears to match '{term}'? [YESNO]"
        if YESNO=='Yes':
            ", [METRIC].\n"
            if METRIC not in selected_metrics:
                selected_metrics.append(METRIC)
        else:
            "Explain in less than 100 words to the user why you are unable to continue with their request.\n"
            "Response: [RESPONSE]"

    common_dimensions = await search_for_dimensions(selected_metrics)
    if not common_dimensions:
        "There are no shared dimensions for these metrics. Explain in less than 100 words to the user why you are unable to continue with their request.\n"
        "Response: [RESPONSE]"

    for dim in common_dimensions:
        _dimensions.append(dim)
        
    "<Group By>\n"
    groupbys=[]
    for i in range(int(GROUPBY_COUNT)):
        "[GROUPBY_TERM]"
        groupbys.append(GROUPBY_TERM.strip("\n '."))
    "</Group By>\n"

    
    
    "<Filter By>\n"
    filters=[]
    for i in range(int(FILTER_COUNT)):
        "[FILTER_TERM]"
        filters.append(FILTER_TERM.strip("\n '."))
    "</Filter By>\n"
    
    common_dimensions = "\n".join(common_dimensions)
    """<Dimensions metrics={', '.join(selected_metrics)}:
    {common_dimensions}
    </Dimensions>"""

    selected_groupbys=[]
    for term in groupbys:
        "Is there a dimension that matches '{term}'? [YESNO]"
        if YESNO=='Yes':
            ", [DIMENSION].\n"
            selected_groupbys.append(DIMENSION)
        else:
            "Explain in less than 100 words to the user why you are unable to continue with their request.\n"
            "Response: [RESPONSE]"

    selected_filters=[]
    for term in filters:
        "Is there a dimension that could be used to filter to '{term}'? [YESNO]"
        if YESNO=='Yes':
            ", [DIMENSION].\n"
            "Write a valid sql filter expression for {term} using {DIMENSION}:\n"
            "<sql filter expression>[FILTER]"
            selected_filters.append(FILTER.split('</')[0])
        else:
            "Explain in less than 100 words to the user why you are unable to continue with their request.\n"
            "Response: [RESPONSE]"

    return await calculate_metric(selected_metrics, selected_groupbys, selected_filters)
    
from
    "chatgpt"
where
    STOPS_AT(METRIC_TERM, "\n") and
    STOPS_AT(GROUPBY_TERM, "\n") and
    STOPS_AT(FILTER_TERM, "\n") and
    STOPS_AT(RESPONSE, "\n") and
    len(RESPONSE)<200 and
    STOPS_AT(FILTER, "</") and 
    METRIC_COUNT in ['0', '1', '2', '3', '4', '5'] and GROUPBY_COUNT in ['0', '1', '2', '3', '4', '5'] and FILTER_COUNT in ['0', '1', '2', '3', '4', '5'] and 
    YESNO in ['Yes', 'No'] and
    METRIC in _metrics and
    DIMENSION in _dimensions
    '''