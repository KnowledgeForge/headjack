import logging
from textwrap import dedent, indent  # noqa: F401
from typing import List, Set, Union

import lmql
from lmql.runtime.bopenai import get_stats

from headjack.agents.examples.metric_calculate_examples import (  # noqa: F401
    get_metric_calculate_examples,
)
from headjack.agents.metric_search import search_for_metrics  # noqa: F401
from headjack.agents.registry import register_agent_function
from headjack.config import get_settings
from headjack.models.utterance import Observation, Response, Utterance
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.basic import strip_whole  # noqa: F401
from headjack.utils.consistency import consolidate_responses
from headjack.utils.semantic_sort import semantic_sort  # noqa: F401

_logger = logging.getLogger("uvicorn")


async def search_for_dimensions(metrics):
    settings = get_settings()
    try:
        metrics = "&".join("metric=" + f.strip("\n '.") for f in metrics)
        _logger.info(f"Searching for dimensions using the metrics service: `{metrics}`")
        results = await fetch(f"{settings.metric_service}/metrics/common/dimensions/?{metrics}", "GET", return_json=True)
        dimension_names = [dimension["name"] for dimension in results]
        return dimension_names
    except Exception as e:
        _logger.info(f"Error while attempting to reach the metric service {str(e)}")
        return "No results"


async def calculate_metric(metrics, dimensions, filters, orderbys, limit=None):
    settings = get_settings()
    metrics = "&".join("metrics=" + f.strip("\n '.") for f in metrics)
    dimensions = set(dimensions)
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


@register_agent_function(
    """
This agent takes a question that requests a numeric value (e.g. metric)
that may include aggregations, filters, orderbys and limiting and actually runs the calculation.
**IMPORTANT: This agent is fully capable, you do not need to search for or otherwise provide a specific metric or data to this agent as it will determine everything necessary to complete your request on its own.**
Use this for questions like:
    calculate the average...
    find the total...
    what is the mean...
    count the number of...
    etc.
""",
)
async def metric_calculate_agent(
    question: Utterance,
    n: int = 1,
    temp: float = 0.0,
    chat_context: bool = False,
) -> Union[Observation, Response]:
    ret = await consolidate_responses(  # type: ignore
        add_source_to_utterances(await _metric_calculate_agent(question, [], set(), n, temp, chat_context), "metric_calculate_agent"),  # type: ignore
    )
    _logger.info(get_stats())
    return ret


@lmql.query
async def _metric_calculate_agent(question: Utterance, _metrics: List[str], _dimensions: Set[str], n: int, temp: float, chat_context: bool) -> Union[Observation, Response]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp, max_len=4096)
        """You are given a User request to calculate a metric.

        ### Here are some examples:
        {get_metric_calculate_examples(question.utterance, 2)}
        ### End of examples

        You must extract the necessary information from the user's query for the api request.
        User: {question.utterance}

        First, reason about the user's query. What are the metrics? Are there any groupings - put them in a numbered list? Is ordering specified or is it required to use with a limit - put them in a numbered list? Are there any filters - put them in a numbered list? Answer these questions and explain your rationale.
        Put your reasoning in reasoning tags `<logic>your reasoning</logic>
        <logic>[REASONING]logic>
        """
        _logger.info(f"Reasoning `{REASONING}`.")
        """
        Count the number of metrics, e.g. terms that describe some calculated number.
        Thought: There's [METRIC_COUNT] metric(s).
        List the terms that describe each metric.
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
                "Explain in less than 50 words to the user why you are unable to continue with their request.\n"
                "Response: [RESPONSE]"
                return Response(utterance=RESPONSE, parent = question)

            metrics = [md['name'] for md in res['metadatas'][0]]
            _metrics += metrics
            metric_texts = [f"{desc}: {m}" for desc, m in zip(res['documents'][0], metrics)]
            metric_results+=metric_texts
        metric_results=indent(dedent("\n".join(metric_results)), ' '*4)
        _logger.info(f"Found metrics `{metric_results}`.")
        "A semantic search returned the following metrics.\n"
        "<MetricResults>\n"
        "{metric_results}"
        "\n</MetricResults>\n"

        selected_metrics=[]
        for term in terms:
            "Explain in just a few words from these MetricResults which seem most likely to match '{term}' and why: [EXPLAIN]\n"
            "Now, based on this explanation - Yes or No - Is there a metric for '{term}' from the MetricResults that seems similar enough or synonomous to be used to calculate it? [YESNO]"
            if YESNO=='Yes':
                ", [METRIC].\n"
                if METRIC not in selected_metrics:
                    selected_metrics.append(METRIC)
            else:
                "Explain in less than 50 words to the user why you are unable to continue with their request including information about the metrics you may have considered.\n"
                "Response: [RESPONSE]"
                return Response(utterance=RESPONSE, parent = question)
        _logger.info(f"Decided metrics `{selected_metrics}`.")
        common_dimensions = await search_for_dimensions(selected_metrics)

        if not common_dimensions:
            if len(selected_metrics)>1:
                "\nThere are no shared dimensions for these metrics.\n"
            else:
                "\nThere are no dimensions for this metric.\n"
            "Explain in less than 50 words to the user why you are unable to continue with their request including information about the metrics you may have considered.\n"
            "Response: [RESPONSE]"
            return Response(utterance=RESPONSE, parent = question)

        for dim in common_dimensions:
            _dimensions.add(dim)
        """
        Count the number of group bys or aggregations from the user query '{question}'.
        Thought: There's [GROUPBY_COUNT] group by dimension(s).
        """
        """
        List the terms that describe each group by. Be certain that you split your lists of terms onto new lines. This means you will have {GROUPBY_COUNT} lines of terms.
        <Group By>
        """
        groupbys=[]
        for i in range(int(GROUPBY_COUNT)):
            "[GROUPBY_TERM]"
            groupbys.append(GROUPBY_TERM.strip("\n '."))
        "</Group By>\n"
        _logger.info(f"Determined groupings of `{groupbys}`.")
        """
        Count the number of order bys or sortings from the user query '{question}'. You only need to order if it is obvious from the query.
        Thought: There's [ORDER_COUNT] order by dimension(s).
        """
        """
        List the terms that describe each orderby. Be certain that you split your lists of terms onto new lines. This means you will have {ORDER_COUNT} lines of terms.
        Include in the terms some description of whether it should be ascending or descending.
        <Order By>
        """
        orderbys=[]
        for i in range(int(ORDER_COUNT)):
            "[ORDERBY_TERM]"
            orderbys.append(ORDERBY_TERM.strip("\n '."))
        "</Order By>\n"
        _logger.info(f"Determined orderings of `{orderbys}`.")

        limit = None
        "Does the user query '{question}' suggest there needs to be a limit? Yes or No. [YESNO]\n"
        if YESNO=='Yes':
            _logger.info(f"Decided there needs to be a limit.")
            "The limit is <limit type=integer>[LIMIT]limit>\n"
            limit = int(strip_whole(LIMIT, '</'))
            _logger.info(f"Deciding to limit to `{limit}` results.")
        else:
            _logger.info(f"Decided there does NOT need to be a limit.")

        filter_consideration=""
        if orderbys:
            filter_consideration+="You have decided to order by "+"; ".join(orderbys)
            if limit:
                filter_consideration+=f" and you chose a limit of {limit}."
            else:
                filter_consideration+="."
        else:
            if limit:
                filter_consideration+=f"You chose a limit of {limit}."
        """
        {filter_consideration}
        With this in mind, determine the number of filters needed from the user query '{question}' not handled by any orderings and limit already determined.
        Thought: There's still [FILTER_COUNT] filter(s) needed.
        """
        """
        Describe each filter. Be certain that you split your lists of terms onto new lines. This means you will have {FILTER_COUNT} lines of terms.
        <Filter By>
        """
        filters=[]
        for i in range(int(FILTER_COUNT)):
            "[FILTER_TERM]"
            filters.append(FILTER_TERM.strip("\n '."))
        "</Filter By>\n"

        selected_groupbys=[]
        for term in groupbys:
            temp_dims=semantic_sort(term, common_dimensions, 10)
            dim_options=indent(dedent("\n".join(temp_dims)), ' '*4)
            """
        <DimensionOptions terms={term}>
        {dim_options}
        </DimensionOptions>
            """
            "\nExplain in just a few words from these DimensionOptions which seem most likely to match '{term}' and why: [EXPLAIN]"
            "\nNow, based on this explanation - Yes or No - Is there a dimension from these DimensionOptions that appears similar enough to be used for aggregating '{term}'?: [YESNO]"

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
                "\nExplain in less than 50 words to the user why you are unable to continue with their request including information about the metrics and the dimensions you may have considered.\n"
                "Response: [RESPONSE]"
                return Response(utterance=RESPONSE, parent = question)

        selected_orderbys=[]
        for term in orderbys:
            temp_dims=semantic_sort(term, common_dimensions+selected_metrics, 10)
            dim_options=indent(dedent("\n".join(temp_dims)), ' '*4)
            """
        <OrderbyOptions terms={term}>
        {dim_options}
        </OrderbyOptions>
            """
            "\nExplain in just a few words from these OrderbyOptions or one of your selected metrics (reminder: you have selected {selected_metrics}) which seem most likely to match '{term}' and why: [EXPLAIN]"
            "\nNow, based on this explanation - Yes or No - Is there a dimension from OrderbyOptions or a selected metric (reminder: you have selected {selected_metrics}) that appears similar enough to be used for ordering '{term}'?: [YESNO]"
            if YESNO=='Yes':
                for dim in list(_dimensions):
                    _dimensions.remove(dim)
                for dim in temp_dims:
                    _dimensions.add(dim)
                ", [DIMENSION].\n"
                "This needs to be ASC ascending or DESC descending: [ASC_DESC]\n"
                selected_orderbys.append(DIMENSION+" "+ASC_DESC)
                _logger.info(f"Adding orderby `{selected_orderbys[-1]}`.")
                for dim in common_dimensions:
                    _dimensions.add(dim)
            else:
                "Explain in less than 50 words to the user why you are unable to continue with their request including information about the metrics and dimensions you may have considered.\n"
                "Response: [RESPONSE]"
                return Response(utterance=RESPONSE, parent = question)
        selected_filters=[]
        for term in filters:
            temp_dims=semantic_sort(term, common_dimensions, 10)
            dim_options=indent(dedent("\n".join(temp_dims)), ' '*4)
            """
        <FilterOptions terms={term}>
        {dim_options}
        </FilterOptions >
            """
            "\nExplain in just a few words from these FilterOptions which seem most likely to match '{term}' and why: [EXPLAIN]"
            "\nAre there any dimensions from FilterOptions that appears similar enough to be used to filter '{term}'? Yes or No.: [YESNO]"
            if YESNO=='Yes':
                for dim in list(_dimensions):
                    _dimensions.remove(dim)
                for dim in temp_dims:
                    _dimensions.add(dim)
                ", and [SQL_FILTER_COUNT] is/are needed.\n"

                "<filter dimensions term={term}>\n"
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
                "<sql filter expression>[FILTER]sql filter expression>"

                selected_filters.append(FILTER.split('</')[0])
                _logger.info(f"Adding filter `{selected_filters[-1]}`.")
            else:
                "Explain in less than 50 words to the user why you are unable to continue with their request including information about the metrics and dimensions you may have considered.\n"
                "Response: [RESPONSE]"
                return Response(utterance=RESPONSE, parent = question)

        results = await calculate_metric(selected_metrics, selected_groupbys, selected_filters, selected_orderbys, limit)
        if results == "Cannot calculate metric":
            return Response(utterance="There was a problem with the metric service, so I cannot calculate `{question.utterance}`.", parent = question)
        RESPONSE=f"Metric calculation complete for `{question.utterance}`."
        if chat_context:
            "The metrics have been calculated. Briefly explain in less than 75 words on a single line to the user all that you have done to complete this request.\n"
            "Response:[RESPONSE]"
        return Observation(utterance=RESPONSE, metadata = results, parent = question, notes="I have stored the data in the workspace for other agents to acquire as needed.")

    from
        "chatgpt"
    where
        STOPS_AT(REASONING, "\n") and
        STOPS_AT(METRIC_TERM, "\n") and
        STOPS_AT(GROUPBY_TERM, "\n") and
        STOPS_AT(ORDERBY_TERM, "\n") and
        STOPS_AT(FILTER_TERM, "\n") and
        STOPS_AT(RESPONSE, "\n") and
        STOPS_AT(FILTER, "</") and
        STOPS_AT(LIMIT, "</") and
        METRIC_COUNT in ['0', '1', '2', '3', '4', '5'] and GROUPBY_COUNT in ['0', '1', '2', '3', '4', '5'] and FILTER_COUNT in ['0', '1', '2', '3', '4', '5'] and ORDER_COUNT in ['0', '1', '2', '3', '4', '5'] and SQL_FILTER_COUNT in ['0', '1', '2', '3'] and
        YESNO in ['Yes', 'No'] and
        ASC_DESC in ['ASC', 'DESC'] and
        METRIC in _metrics and
        DIMENSION in _dimensions
    '''
