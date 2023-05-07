"""
An agent that can handle common tasks

"Are there any metrics about..."
"Are there any metrics pertaining to..."
"Tell me about this metric..."
"Are these metrics compatible"
"Tell me about the dimensions that are available for metric x..."
"""
from typing import Set, Type, cast
from textwrap import indent
from headjack.agents.query_templates.standard import standard_query
from headjack.models.agent import Agent
from headjack.models.utterance import Answer, User, Utterance


class StandardAgent(Agent):
    "A standard agent that can answer queries and solve tasks with tools."

    def __init__(
        self,
        *,
        description: str = "",
        ref_name: str = "standard",
        query=standard_query,
        loop_limit: int = 5,
        history_length: int = 3,
        history_utterances: Set[Type[Utterance]] = {User, Answer},
        **kwargs,
    ):
        super().__init__(
            query=query,
            description=description or cast(str, StandardAgent.__doc__),
            ref_name=ref_name,
            **kwargs,
        )
        self.loop_limit = loop_limit
        self.history_length = history_length
        self.history_utterances = history_utterances
        self.tools_prompt = "\n".join(indent("tool.name"+": " +tool.description.replace('\n', ' '), ' '*8) for tool in self.tools)
        self.tool_refs = {tool.name: tool for tool in self.tools}
        tool_body = []
        for tool in self.tools:
            tool_body.append(f"if TOOL=='{tool.name}':")
            tool_body.append(indent(f'"Tool Input: \\n"{tool.schema.body()}\n', ' '*20))
            tool_body.append(
                indent(f"action = Action(utterance_ = {tool.schema.payload_code()}, agent = agent, parent_ = tool_choice); await agent.asend(action)", ' '*20)  # noqa: E501
            )
            tool_body.append(
                indent("observation = await agent.tool_refs.get(TOOL)(action); observation.parent = action; await agent.asend(observation)", ' '*20)# noqa: E501
            )
            tool_body.append(indent(r"'{observation}\n'", ' '*16))
        self.tool_body = "\n".join(tool_body)
        self.tool_conditions = " and ".join(tool.schema.where() for tool in self.tools)
        self.tool_names = list(self.tool_refs.keys())
        self._run = self._compile_query(self.query)

    async def __call__(self, user: User):
        return await self.run(user, self.history_length, self.history_utterances, self.loop_limit, [], [])
