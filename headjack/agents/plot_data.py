import json
import logging
from textwrap import dedent
from typing import Any, Dict, List, Optional, TypedDict, Union, cast

import lmql
import plotly.express as px  # noqa: F401

from headjack.agents.registry import register_agent_function
from headjack.models.utterance import Answer, Observation, Response, Utterance
from headjack.utils.consistency import consolidate_responses

_logger = logging.getLogger("uvicorn")


class PlotDataColumn(TypedDict):
    name: str
    type: str
    values: List[Any]


def utterance_is_data(utterance: Utterance) -> Union[bool, List[PlotDataColumn]]:
    try:
        columns = utterance.metadata["results"][0]["columns"]
        if 'rows' in utterance.metadata["results"][0]:
            for row in utterance.metadata["results"][0]['rows']:
                for i, col in enumerate(columns):
                    col['values'] = col.get('values') or []
                    col['values'].append(row[i])
        return columns
    except Exception:
        return False


def code_valid(cols: List[PlotDataColumn], code: str) -> Optional[Exception]:
    df: Dict[str, list] = {col["name"]: [] for col in cols}  # noqa: F841
    code = dedent(code) + "\nfig"
    try:
        exec(code)
        return None
    except Exception as exc:
        return exc


def plot_json(cols: List[PlotDataColumn], code: str) -> dict:
    df = {col["name"]: [] if 'values' not in col else col['values'] for col in cols}  # type: ignore
    code = dedent(code) + "\nret=fig.to_json()"
    exec(code)
    return json.loads(locals()["ret"])


@register_agent_function(
    """This agent takes a request such as 'make a bar plot' WITHOUT providing any data and creates a plot using plotly express.
    **IMPORTANT: no explicit data is needed to be provided to this agent and no search is generally necessary**
    Data will be automatically deduced by the specialist.
    It can create any plot that plotly express can.
    """,
)
async def plot_data_agent(question: Utterance, n: int = 1, temp: float = 0.0) -> Union[Observation, Response]:
    return await _plot_data_agent(question, n, temp)

async def _plot_data_agent(question: Utterance, n: int = 1, temp: float = 0.0) -> Union[Observation, Response]:
    cols = None
    for utterance in question.history():
        is_data = utterance_is_data(utterance)
        if is_data is not False:
            cols = is_data
    if cols is None:
        ret = Response(utterance="There was no data in the conversation history to plot.", parent=question)
        ret.source = "plot_data"
        return ret
    cols = cast(List[PlotDataColumn], cols)
    code = await _plot_data(cols, question, n, temp)
    if isinstance(code, Response):
        code.parent = question
        return code
    ret = Observation(utterance= code.utterance, metadata=plot_json(cols, code.metadata['code']), parent=question)
    ret.source = "plot_data"
    return ret


async def _plot_data(cols: List[PlotDataColumn], question: Utterance, n: int, temp: float) -> Union[Answer, Response]:
    response = await consolidate_responses(await _plot_data_prompt(cols, question, n, temp))  # type: ignore
    return response


# fmt: off
@lmql.query
async def _plot_data_prompt(cols: List[PlotDataColumn], question: Utterance, n: int, temp: float) -> Union[Answer, Response]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp, max_len=3000)
        """You are given the following request to plot some data.
        Request: {question.utterance}
        The data you will plot is in a dictionary {{columns: lists of data}} `df`. plotly express is available as px.
        """
        data_info = "\n".join(f'{col["name"]}: {col["type"]}' for col in cols)
        """
        Here is some info on the data:
        Column Name: Column Type
        {data_info}

        You MUST do your best to complete the request. If there is information for the design of the plot missing in the request, you MUST try to complete it yourself.
        What kind of plot and relevant attributes are needed to complete this request? Keep your thought as short as possible.
        Thought: To create a plotly express plot for this request, [THOUGHT]

        Generate some valid python plotly express code within the code block to plot `df` as `fig` according to the request.
        Do not show `fig`.:
        """
        for _ in range(5):# 5 tries
            """
        ```python
        import plotly.express as px[CODE]
        ```
            """
            code = CODE.strip('`')
            code =code.split("\n")
            code = "\n".join([code[0][1:] if code[0][0]==' ' else code[0], *code[1:]])
            _logger.info(f"Plot attempt: {code}")

            if exc:=code_valid(cols, code):
                _logger.info(f"{exc}")
                """
            Your code failed with the following python error:
                {exc}
            Make corrections to address the error and try again:
                """
            else:
                "\nExplain in a few words why you were unable to complete the request:\n[EXPLANATION]"
                return Answer(utterance= EXPLANATION, metadata={"code":code})
        "\nExplain in a few words why you were unable to complete the request:\n[EXPLANATION]"
        return Response(utterance=EXPLANATION)

    FROM
        "chatgpt"
    WHERE
        METHOD in PLOTLY_METHODS and
        STOPS_AT(CODE, '`')
    '''
