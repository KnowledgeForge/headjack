"""
Standard react query
"""
from headjack.models.agent import Agent
from headjack.models.utterance import Utterance


async def standard_query(
    agent: Agent,
    utterance: Utterance,
    history_length,
    history_utterances,
    loop_limit,
    thought_filter,
    tool_filter,
):
    '''lmql
    {decoder}
        """
        You are a chatbot Agent that helps users answer questions.
        Agent answers are clear, concise and complete. Information the agent uses after an obervation should be about the observation without hallucination.
        Agent NEVER uses marker phrases like User:, Thought:, Observation:, Action:, Answer: as these are used by the system.

        The Agent uses thoughful reasoning like so:

            Thought: I should use a tool.
            Tool: Agent selects appropriate tool
            Tool Input: thoroughly descriptive input for the tool to work.
            Observation: some information that may help respond to the user.
            ...
            Thought: I can answer the user now.
            Answer: Agent describes the answer
            OR
            Thought: I have tried all my tools and still could not find an answer.
            Answer: Agent says it could not find an answer



        Here are the tools you may choose from:
        {tools_prompt}

        Conversation:
        {{utterance.convo(history_length, history_utterances)}}"""

        # "Come up with a short problem description and plan for what the user has said.\\n"
        # "Problem: [PROBLEM]\\n"
        # problem = Thought(utterance_ = PROBLEM, agent = agent, parent_ = utterance)
        # await agent.asend(problem)
        # "Plan: [PLAN]\\n"
        # plan = Thought(utterance_ = PLAN, agent = agent, parent_ = problem)
        # await agent.asend(plan)
        
        for _ in range(loop_limit):
            "Thought: [THOUGHT]\\n"
            thought = Thought(utterance_ = THOUGHT, agent = agent, parent_ = plan)
            await agent.asend(thought)
            retry_tool = False
            if retry_tool or THOUGHT == 'I should use a tool.':
                tool_payloads=dict()
                "Tool: [TOOL]\\n"
                tool_choice = Thought(utterance_ = "I will use my "+TOOL, agent = agent, parent_=thought)
                await agent.asend(tool_choice)
                # import pdb; pdb.set_trace()
                {tool_body}
            elif THOUGHT.startswith('I can answer the user'):
                "Agent NEVER uses marker phrases like User:, Thought:, Observation:, Action:, Answer: as these are used by the system. "
                "Answers are concise and at most 200 words unless content is verbatim from observations.\\n"
                "Answer: [ANSWER]\\n"
                answer = Answer(utterance_ = ANSWER, agent = agent, parent_ = tool_choice)
                await agent.asend(answer)
                break
            else:
                answer = Answer(utterance_ = "I apologize, but I did not find an answer.", agent = agent, parent_ = thought)
                await agent.asend(answer)
                break
        await agent.asend(None)
    from
        "{model_identifier}"
    where
        THOUGHT in [
            thought
            for thought in [
                    "I should use a tool.",
                    'I can answer the user now by summarizing information from the conversation.',
                    'I can answer the user now by extracting information from the conversation history.',
                    'I can answer the user now by extracting information from the memory.',
                    'I can answer the user now based on this latest information.',
                    "I have tried all my tools and still could not find an answer."
                ]
            if thought not in thought_filter
        ] and
        TOOL in [
            tool
            for tool in {tool_names}
            if tool not in tool_filter
        ] and
        len(ANSWER)<500 and
        STOPS_AT(THOUGHT, "\\n") and
        STOPS_AT(TOOL, "\\n") and
        # STOPS_AT(PROBLEM, "\\n") and
        # STOPS_AT(PLAN, "\\n") and
        {tool_conditions}
    '''
