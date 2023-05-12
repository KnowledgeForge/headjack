from headjack.models.tool import HTTPVerb, Tool, ToolSchema

metric_dimension_search_schema = ToolSchema(
    url="http://localhost:8000/metrics/common/dimensions",
    verb=HTTPVerb.GET,
    name="Metric Dimension Search",
    description="Tool used to search for dimensions that can be used with a selected metric.",
    parameters=[
        {
            "name": "metric",
            "description": "Metric to search for compatible dimension columns for.",
            "type": "string",
            "options": {"ref": "Metric Search.results.ref_name"},
        },
    ],
    results={"type": "string", "max_length": 100},
)

metric_dimension_search = Tool(metric_dimension_search_schema)
