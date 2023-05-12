from headjack.models.tool import HTTPVerb, Tool, ToolSchema

knowledge_search_schema = ToolSchema(
    url="http://0.0.0.0:16410/query",
    verb=HTTPVerb.GET,
    name="Knowledge Search",
    description="Tool used to search for general knowledge. Asking a question will return documents containing relevant information.",
    parameters=[
        {
            "name": "text",
            "description": "A succinct piece of text that asks a targeted question to find relevant knowledge documents. Example: Who is the president of the DJ Roads Company?",
            "type": "string",
            "max_value": 100,
        },
        {"name": "collection", "type": "string", "options": ["knowledge"]},
    ],
    results={"type": "string", "max_length": 100},
    code="""
def process_observation(action_input, observation_input):
    return [i for j in observation_input['documents'] for i in j]
""",
    examples=["Who is the president of DJ Roads?"]
)
knowledge_search = Tool(knowledge_search_schema)
