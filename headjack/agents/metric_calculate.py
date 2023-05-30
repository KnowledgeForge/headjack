import logging
from typing import List, Set

import lmql

from headjack.agents.metric_search import search_for_metrics  # noqa: F401
from headjack.config import get_settings
from headjack.utils.general import fetch
from textwrap import dedent, indent
from headjack.utils.semantic_sort import semantic_sort # noqa: F401

_logger = logging.getLogger("uvicorn")


async def search_for_dimensions(metrics):
    settings = get_settings()
    try:
        metrics = "&".join("metric=" + f.strip("\n '.") for f in metrics)
        _logger.info("Searching for dimensions using the metrics service")
        results = await fetch(f"{settings.metric_service}/metrics/common/dimensions/?{metrics}", "GET", return_json=True)
        return results
    except Exception as e:
        _logger.info(f"Error while attempting to reach the metric service {str(e)}")
        return "No results"


async def calculate_metric(metrics, dimensions, filters, orderbys, limit=None):
    settings = get_settings()
    metrics = "&".join("metrics=" + f.strip("\n '.") for f in metrics)
    dimensions = set(dimensions)|set(orderbys)
    dimensions = "&".join("dimensions=" + f.strip("\n '.") for f in dimensions)
    filters = "&".join("filters=" + f.strip("\n '.") for f in filters)
    orderbys = set(orderbys)
    orderbys = "&".join("orderby=" + f.strip("\n '.") for f in orderbys)
    url = f"{settings.metric_service}/data/?"
    url += metrics
    if dimensions.strip():
        url += "&" + dimensions
    if filters.strip():
        url += "&" + filters
    if orderbys.strip():
        url += "&" + orderbys
    if limit is not None:
        url += f"&limit={limit}"

    try:
        _logger.info(f"Calculating metric using the metrics service {url}")
        results = await fetch(url, "GET", return_json=True)
    except Exception as e:
        _logger.info(f"Error while attempting to reach metrics service {str(e)}")
        return "Cannot calculate metric"
    return results


async def metric_calculate_agent(question: str):
    return await _metric_calculate_agent(question, [], set())

@lmql.query
async def _metric_calculate_agent(question: str, _metrics: List[str], _dimensions: Set[str]):
    '''lmql
argmax
    """You are given a User request to calculate a metric using a tool. 

    Here are some examples:
        User: What is the average temperature by city for the month of July where the city's population is more than 10 million?
        Count the number of metrics, group by dimensions, filters, order bys and whether there is a limit.
        Thought: There's 1 metric(s), 1 group by dimension(s), 2 filter(s), 0 order by(s) and no limit being requested.
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
        Are there any dimensions that could be used to filter 'month is July'?: Yes, and there's 1 needed.
        <filter dimensions>
        location.month
        </filter dimensions>
        Write a valid sql filter expression for 'month is July'.
        You must use only location.month without splitting the names: 
        <sql filter expression>location.month='July'</sql filter expression>
        Are there any dimensions that could be used to filter 'population more than 10 million'?: Yes, and there's 1 needed.
        <filter dimensions>
        location.population
        </filter dimensions>
        Write a valid sql filter expression for 'population more than 10 million'.
        You must use only location.population without splitting the names: 
        <sql filter expression>location.population>10000000</sql filter expression>
        # Request is run successfully and results sent to the user    

        User: What is the average rating and number of reviews for the top 10 highest selling products sold in the same month as they were stocked?
        Count the number of metrics, group by dimensions, filters, order bys and whether there is a limit.
        Thought: There's 2 metric(s), 0 group by dimension(s), 1 filter(s), 1 order by(s) and a limit being requested.
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
        <Order By>
        highest selling products, top sellers
        </Order By>
        <Filter By>
        products sold in the same month as stocked
        </Filter By>
        <Dimensions metrics=avg_rating, num_reviews>
        item.name
        item.sold_month
        item.category
        item.id
        item.stocked_month
        item.sales
        ...
        store.name
        store.id
        store.location
        </Dimensions>
        Is there a dimension that matches 'highest selling products, top sellers'?: Yes, item.sales.
        Are there any dimensions that could be used to filter 'products sold in the same month as stocked'?: Yes, and 2 is/are needed.
        <filter dimensions>
        item.sold_month
        item.stocked_month
        </filter dimensions>
        Write a valid sql filter expression for 'products sold in the same month as stocked'.
        You must use only item.sold_month, item.stocked_month without splitting the names: 
        <sql filter expression>item.sold_month = item.stocked_month</sql filter expression>
        There needs to be a limit. This is an integer value. The limit should be 10.
        # Response sent to user
    
    
    User: {question}
    Count the number of metrics, group by dimensions, filters, order bys and whether there is a limit.
    Thought: There's [METRIC_COUNT] metric(s), [GROUPBY_COUNT] group by dimension(s), [FILTER_COUNT] filter(s), [ORDER_COUNT] order by(s) and [LIMIT_Q] limit.
    <Metric Terms>
    """
    _logger.info(f"User query `{question}`.")
    terms=[]
    for i in range(int(METRIC_COUNT)):
        "[METRIC_TERM]"
        terms.append(METRIC_TERM.strip("\n '."))
    "</Metric Terms>\n"
    metric_results = []
    for term in terms:
        res = await search_for_metrics(term)
        if res=='No results':
            "No results were found searching for {term}. The search server may be down or no metrics met a relevance threshold."
            "Explain in less than 100 words to the user why you are unable to continue with their request.\n"
            "Response: [RESPONSE]"
            return RESPONSE
            
        metrics = [md['name'] for md in res['metadatas'][0]]
        _metrics += metrics
        metric_texts = [f"{desc}: {m}" for desc, m in zip(res['documents'][0], metrics)]
        metric_results+=metric_texts
    metric_results=indent(dedent("\n".join(metric_results)), ' '*4)
    _logger.info(f"Found metrics `{metric_results}`.")
    
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
            return RESPONSE

    common_dimensions = await search_for_dimensions(selected_metrics)
    if not common_dimensions:
        "There are no shared dimensions for these metrics. Explain in less than 100 words to the user why you are unable to continue with their request.\n"
        "Response: [RESPONSE]"
        return RESPONSE

    for dim in common_dimensions:
        _dimensions.add(dim)
        
    "<Group By>\n"
    groupbys=[]
    for i in range(int(GROUPBY_COUNT)):
        "[GROUPBY_TERM]"
        groupbys.append(GROUPBY_TERM.strip("\n '."))
    "</Group By>\n"

    "<Order By>\n"
    orderbys=[]
    for i in range(int(ORDER_COUNT)):
        "[ORDERBY_TERM]"
        orderbys.append(ORDERBY_TERM.strip("\n '."))
    "</Order By>\n"
    
    "<Filter By>\n"
    filters=[]
    for i in range(int(FILTER_COUNT)):
        "[FILTER_TERM]"
        filters.append(FILTER_TERM.strip("\n '."))
    "</Filter By>\n"
    

    selected_groupbys=[]
    for term in groupbys:
        temp_dims=semantic_sort(term, common_dimensions, 10)
        dim_options=indent(dedent("\n".join(temp_dims)), ' '*4)
        """<Dimensions terms={term}>
        {dim_options}
        </Dimensions>
        """
        "Is there a dimension that matches '{term}': [YESNO]"
        
        if YESNO=='Yes':
            for dim in list(_dimensions):
                _dimensions.remove(dim)
            for dim in temp_dims:
                _dimensions.add(dim)
            ", [DIMENSION].\n"
            selected_groupbys.append(DIMENSION)
            _logger.info(f"Adding groupby `{selected_groupbys[-1]}`.")
            for dim in common_dimensions:
                _dimensions.add(dim)
        else:
            "Explain in less than 100 words to the user why you are unable to continue with their request.\n"
            "Response: [RESPONSE]"
            return RESPONSE

    selected_orderbys=[]
    for term in orderbys:
        temp_dims=semantic_sort(term, common_dimensions, 10)
        dim_options=indent(dedent("\n".join(temp_dims)), ' '*4)
        """<Dimensions terms={term}>
        {dim_options}
        </Dimensions>
        """
        "Is there a dimension that matches '{term}': [YESNO]"
        if YESNO=='Yes':
            for dim in list(_dimensions):
                _dimensions.remove(dim)
            for dim in temp_dims:
                _dimensions.add(dim)
            ", [DIMENSION].\n"
            selected_orderbys.append(DIMENSION)
            _logger.info(f"Adding orderby `{selected_orderbys[-1]}`.")
            for dim in common_dimensions:
                _dimensions.add(dim)
        else:
            "Explain in less than 100 words to the user why you are unable to continue with their request.\n"
            "Response: [RESPONSE]"
            return RESPONSE
            
    selected_filters=[]
    for term in filters:
        temp_dims=semantic_sort(term, common_dimensions, 10)
        dim_options=indent(dedent("\n".join(temp_dims)), ' '*4)
        """<Dimensions terms={term}>
        {dim_options}
        </Dimensions>
        """
        "Are there any dimensions that could be used to filter '{term}'? [YESNO]"
        if YESNO=='Yes':
            for dim in list(_dimensions):
                _dimensions.remove(dim)
            for dim in temp_dims:
                _dimensions.add(dim)
            ", and [SQL_FILTER_COUNT] is/are needed.\n"
            "<filter dimensions>\n"
            curr_dims = []
            for i in range(int(SQL_FILTER_COUNT)):
                "[DIMENSION]\n"
                curr_dims.append(DIMENSION)
            "</filter dimensions>"
            for dim in common_dimensions:
                _dimensions.add(dim)
            curr_dims=", ".join(curr_dims)
            "Write a valid sql filter expression for {term}.\n"
            "You must use only {curr_dims} without splitting the names (i.e. a.b must always remain a.b treated as a single name everywhere):\n"
            "<sql filter expression>[FILTER]"
            selected_filters.append(FILTER.split('</')[0])
            _logger.info(f"Adding filter `{selected_filters[-1]}`.")
        else:
            "Explain in less than 100 words to the user why you are unable to continue with their request.\n"
            "Response: [RESPONSE]"
            return RESPONSE
    
    limit = None
    if LIMIT_Q=='a':
        "There needs to be a limit. This is an integer value. The limit should be [LIMIT]"
        _logger.info(f"Deciding to limit to {LIMIT} results.")
        limit = int(LIMIT)
        
    # return await calculate_metric(selected_metrics, selected_groupbys, selected_filters, selected_orderbys, limit)
    
from
    "chatgpt"
where
    STOPS_AT(METRIC_TERM, "\n") and
    STOPS_AT(GROUPBY_TERM, "\n") and
    STOPS_AT(ORDERBY_TERM, "\n") and
    STOPS_AT(FILTER_TERM, "\n") and
    STOPS_AT(RESPONSE, "\n") and
    len(RESPONSE)<200 and
    STOPS_AT(FILTER, "</") and 
    METRIC_COUNT in ['0', '1', '2', '3', '4', '5'] and GROUPBY_COUNT in ['0', '1', '2', '3', '4', '5'] and FILTER_COUNT in ['0', '1', '2', '3', '4', '5'] and ORDER_COUNT in ['0', '1', '2', '3', '4', '5'] and SQL_FILTER_COUNT in ['0', '1', '2', '3'] and 
    YESNO in ['Yes', 'No'] and
    LIMIT_Q in ['no', 'a'] and
    METRIC in _metrics and
    DIMENSION in _dimensions and
    INT(LIMIT)
    '''