from headjack.models.tool import HTTPVerb, Tool, ToolSchema

metric_calculate_schema = ToolSchema(
    url="http://localhost:8000/data",
    verb=HTTPVerb.GET,
    name="Metric Calculate",
    description="Tool used to calculate the value of a metric. Choose a metric and at least some dimension or filter. Examples: calculate the value of, tell me the average, tell me the total, count the number of, ...",
    parameters=[
        {
            "name": "metrics",
            "description": "Metric to search for compatible dimension columns for.",
            "type": "string",
            "options": {"ref": "Metric Dimension Search.parameters[0]"},
        },
        {
            "name": "dimensions",
            "description": "Columns to select to group by. A table.column selection from the metric dimension search results. may only be used if groupby1 is used.",
            "type": "string",
            "options": {"ref": "Metric Dimension Search.results"},
            "min_length": 0,
            "max_length": 3
        },
        {
            "name": "filters",
            "description": """
SQL filter expressions using dimension columns from Metric Dimension Search results. 
Used only when asked a query that requires filtering/subselection such as `where something is...`, `for the...`, `filter by...` or synonymous statements.
These values must be valid SQL filter expressions.
""",
            "type": "string",
            "max_length": 3,
            "min_length": 0,
            "max_value": 50,
            # "required": False,
        },
    ],
    feedback_retries=1,
    result_answer=True,
    results={"type": "string"},
    code="""
def process_action(action_input):
    params=action_input['parameters']
    if not params[1] and not params[2]:
        raise ValueError("at least one of 'dimension' or 'filters' is required")
    try:
        from sqlglot import parse
        for p in params[2]:
            parse(p)
    except:
        raise ValueError(f"The sql filters you provided `{params[2]}` are not valid sql filter expressions. re-evaluate them.")
    return action_input

def process_observation(action_input, observation_input):
    return str(observation_input['results'])
""",
)

metric_calculate = Tool(metric_calculate_schema)
