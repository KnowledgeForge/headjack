import logging
from typing import Union, Optional, List, Any

import lmql
import re
from headjack.agents.registry import register_agent_function
from headjack.models.utterance import ( 
    Action,
    Answer,
    Observation,
    Response,
    Utterance,
)
from textwrap import dedent, indent
from headjack.utils import fetch
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.consistency import consolidate_responses
from io import StringIO
_logger = logging.getLogger("uvicorn")
import plotly.express as px# noqa: F401
import pandas as pd
from typing import Any, List, TypedDict, Dict
import pandas as pd

class PlotDataColumn(TypedDict):
    name: str
    type: Optional[str] = None

class PlotData(TypedDict):
    columns: List[PlotDataColumn]
    rows: List[Any]
    
    @staticmethod
    def to_df(plot_data: Dict[str, Any]) -> pd.DataFrame:
        columns = plot_data['columns']
        cols = [col['name'] for col in columns]
        return pd.DataFrame(dict(zip(cols, plot_data['rows'])))
    
def data_info(df: pd.DataFrame)-> str:
    buffer = StringIO()
    df.info(verbose=True, buf=buffer)
    return buffer.getvalue()

def utterance_is_data(utterance: Utterance)->Union[bool, pd.DataFrame]:
    try:
        return PlotData.to_df(utterance.utterance['results'])
    except:
        return False

def code_valid(df, code: str)->Optional[Exception]:
    try:
        eval(code)
    except Exception as exc:
        return exc

def plot_json(df, code: str)->str:
    return eval(code).to_json()


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
        ret= Response(utterance="There was no data in the conversation history to plot.", parent_=question)
        ret.source = 'plot_data'
        return ret
    
    code = await _plot_data(df, question, n, temp)
    if isinstance(code, Response):
        code.parent_=question
        return code
    ret= Answer(utterance=plot_json(df, code['code']), parent_=question)
    ret.source = 'plot_data'
    return ret

async def _plot_data(df: pd.DataFrame, question: Utterance, n: int, temp: float) -> Union[Action, Response]:
    res=await _plot_data_prompt(df, question, n, temp, [])
    import pdb; pdb.set_trace()
    response = await consolidate_responses(await _plot_data_prompt(df, question, n, temp, []))  # type: ignore
    if isinstance(response, Answer):
        return Action(utterance={'code': response.utterance})
    return response

PLOTLY_METHODS = [method for method in dir(px) if method[0].islower()]

@lmql.query
async def _plot_data_prompt(df: pd.DataFrame, question: Utterance, n: int, temp: float, _restricted_methods: List[str]) -> Union[Answer, Response]:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp, max_len=3000)
        """You are given a request to plot some data.
        
        Example:
            Request: create a scatter plot of the data
            
            The data you will plot is in a pandas dataframe `df`. the plotly.express is available as `px`.
            
            Here is some info on the data:
            <class 'pandas.core.frame.DataFrame'>
            RangeIndex: 3 entries, 0 to 2
            Data columns (total 2 columns):
            #   Column  Non-Null Count  Dtype
            ---  ------  --------------  -----
            0   col1    3 non-null      int64
            1   col2    3 non-null      int64
            dtypes: int64(2)
            memory usage: 176.0 bytes
            
            What plot would you like to use: px.scatter
            
            Generate some plotly express code within <code>your plotly express code</code> to plot df according to the request:
            ```python
            px.scatter(df, x="x", y="y")
            ```

        
        Request: {question.utterance}
        
        The data you will plot is in a pandas dataframe `df`.
        
        Here is some info on the data:
        {data_info(df)}
        
        Here are some methods to choose from: {', '.join(PLOTLY_METHODS)}
        
        What different methods seem most relevant for the Request and you would like to know more about:
        """
        for _ in range(3):
            "- [METHOD]"
            if METHOD in PLOTLY_METHODS and METHOD not in _restricted_methods:
                _restricted_methods.append(METHOD)
                doc = re.search(r'^.*?(?=\n\s*\n)', getattr(px, METHOD).__doc__, re.DOTALL)
                desc = None
                if doc:
                    desc = indent(dedent(doc.group(0).strip()), " "*4)
                if desc is not None:
                    ":\n{desc}\n"
            
            
        
        
        "Based on these descriptions, what method of {_restricted_methods} would best be used to satisfy the request `{question.utterance}`: [RESTRICTED_METHOD]\n"
        docstring = getattr(px, RESTRICTED_METHOD).__doc__[:3000]
        """
        Here is part of the docstring for this method:
        {docstring}
        
        Generate some python plotly express code within the code block to plot df according to the request:
        """
        for _ in range(5):# 5 tries
            """
            ```python
            px.{RESTRICTED_METHOD}(data_frame = df, [CODE]
            ``
            """
            code = f"px.{RESTRICTED_METHOD}(data_frame = df, {CODE.strip('`').strip()}"
            _logger.info(f"Plot attempt: {code}")

            if exc:=code_valid(df, code):
                _logger.info(f"{exc}")
                """
            Your code failed with the following python error:
                {exc}
            Make corrections to address the error and try again:
                """
            else:
                return Answer(utterance=code)
        # return Response(utterance="Failed to generate a plot.")
       
    FROM
        "chatgpt"
    WHERE
        METHOD in PLOTLY_METHODS and
        RESTRICTED_METHOD in _restricted_methods and
        STOPS_AT(CODE, '`')
    '''
