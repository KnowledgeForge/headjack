from headjack.models.tool import HTTPVerb, Tool, ToolSchema

metric_search_schema = ToolSchema(
    url="http://0.0.0.0:16410/query",
    verb=HTTPVerb.GET,
    name="Metric Search",
    description="Tool used to search for metrics. Asking a question will return documents containing relevant information.",
    parameters=[
        {
            "name": "text",
            "description": "Short sequence of words to find relevant metrics.",
            "type": "string",
            "max_value": 50,
        },
        {"name": "collection", "type": "string", "options": ["metrics"]},
    ],
    results={
        "name": {"type": "string", "max_length": 100},
        "ref_name": {"type": "string", "max_length": 100},
        "query": {"type": "string", "max_length": 100},
    },
    code="""
def process_observation(action_input, observation_input):
    return {'name': observation_input['documents'][0], 'ref_name': [m['name'] for m in observation_input['metadatas'][0]], 'query': [m['query'] for m in observation_input['metadatas'][0]]}
""",
)

metric_search = Tool(metric_search_schema)
