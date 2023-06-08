import logging
from io import StringIO
from textwrap import dedent
from typing import Any, List, Optional, Union

import lmql

from headjack.agents.registry import register_agent_function
from headjack.models.utterance import Action, Answer, Observation, Response, Utterance
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.consistency import consolidate_responses

_logger = logging.getLogger("uvicorn")
from typing import Any, Dict, List, TypedDict

import pandas as pd
import plotly.express as px  # noqa: F401


class PlotDataColumn(TypedDict):
    name: str
    type: Optional[str] = None


class PlotData(TypedDict):
    columns: List[PlotDataColumn]
    rows: List[Any]

    @staticmethod
    def to_df(plot_data: Dict[str, Any]) -> pd.DataFrame:
        columns = plot_data["columns"]
        cols = [col["name"] for col in columns]
        return pd.DataFrame(dict(zip(cols, plot_data["rows"])))


def data_info(df: pd.DataFrame) -> str:
    buffer = StringIO()
    df.info(verbose=True, buf=buffer)
    return buffer.getvalue()


def utterance_is_data(utterance: Utterance) -> Union[bool, pd.DataFrame]:
    try:
        return PlotData.to_df(utterance.utterance["results"])
    except:
        return False


def code_valid(df, code: str) -> Optional[Exception]:
    code = dedent(code) + "\nfig"
    try:
        exec(code)
    except Exception as exc:
        return exc


def plot_json(df, code: str) -> str:
    code = dedent(code) + "\nret=fig.to_json()"
    exec(code)
    return locals()["ret"]


@register_agent_function(
    """This function takes a request such as 'make a bar plot of the average repair price' WITHOUT providing any data and creates a plot using plotly express. Data can be automatically deduced.""",
)
async def plot_data(question: Utterance, n: int = 1, temp: float = 0.0) -> Union[Answer, Response]:
    df = None
    for utterance in question.history():
        is_data = utterance_is_data(utterance)
        if is_data is not False:
            df = is_data
    if df is None:
        ret = Response(utterance="There was no data in the conversation history to plot.", parent_=question)
        ret.source = "plot_data"
        return ret

    code = await _plot_data(df, question, n, temp)
    if isinstance(code, Response):
        code.parent_ = question
        return code
    ret = Answer(utterance=plot_json(df, code), parent_=question)
    ret.source = "plot_data"
    return ret


async def _plot_data(df: pd.DataFrame, question: Utterance, n: int, temp: float) -> Union[str, Response]:
    response = await consolidate_responses(await _plot_data_prompt(df, question, n, temp))  # type: ignore
    if isinstance(response, Answer):
        return response.utterance
    return response


PLOTLY_METHODS = [
    "bar",
    "choropleth",
    "density_contour",
    "density_heatmap",
    "histogram",
    "line",
    "scatter",
    "scatter_3d",
    "scatter_geo",
    "scatter_mapbox",
    "box",
    "bar",
    "choropleth_mapbox",
    "density_mapbox",
    "funnel",
    "funnel_area",
    "line_3d",
    "line_geo",
    "line_mapbox",
    "line_polar",
    "line_ternary",
    "parallel_categories",
    "parallel_coordinates",
    "pie",
    "scatter_matrix",
    "violin",
]
# fmt: off
@lmql.query
async def _plot_data_prompt(df: pd.DataFrame, question: Utterance, n: int, temp: float) -> Union[Answer, Response]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp, max_len=3000)
        """You are given the following request to plot some data.
        Request: {question.utterance}
        The data you will plot is in a pandas dataframe `df`. plotly express is available as px.
        Here is some info on the data:
        {data_info(df)}
        Thought: To create a plotly express plot for this request, I should [THOUGHT]

        What are a few different methods seem most relevant for the Request and you would like to know more about:
        """

        "Based on these descriptions, what method of would best be used to satisfy the request `{question.utterance}`: [METHOD]\n"
        docstring = getattr(px, METHOD).__doc__[:3000]

        """
        Here is part of the docstring for this method:
        {docstring}

        Generate some valid python plotly express code within the code block to plot `df` as `fig` according to the request. Do not show the fig.:
        """
        for _ in range(5):# 5 tries
            """
        ```python
        import plotly.express as px
        [CODE]
        ``
            """
            code = CODE.strip('`')
            _logger.info(f"Plot attempt: {code}")

            if exc:=code_valid(df, code):
                print(exc)
                _logger.info(f"{exc}")
                """
            Your code failed with the following python error:
                {exc}
            Make corrections to address the error and try again:
                """
            else:
                return Answer(utterance=code)
        return Response(utterance="Failed to generate a plot.")

    FROM
        "chatgpt"
    WHERE
        METHOD in PLOTLY_METHODS and
        STOPS_AT(CODE, '`')
    '''
