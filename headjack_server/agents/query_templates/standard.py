"""
Standard react query
"""

from headjack_server.models.agent import Agent
from headjack_server.models.utterance import Utterance


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

        Here are the tools you choose from:
        {tools_prompt}

        Conversation:
        {{utterance.convo(history_length, history_utterances)}}"""
        
        for _ in range(loop_limit):
            "Thought: [THOUGHT]\\n"
            thought = Thought(utterance_ = THOUGHT, agent = agent, parent_ = utterance)
            print(thought)
            await agent.asend(thought)
            if THOUGHT == 'I should use a tool.':
                "Tool: [TOOL]\\n"
                tool_choice = Thought(utterance_ = "I will use my "+TOOL, agent = agent, parent_=thought)
                print(tool_choice)
                await agent.asend(tool_choice)
                {tool_body}
            elif THOUGHT.startswith('I can answer the user'):
                "Answer: [ANSWER]\\n"
                answer = Answer(utterance_ = ANSWER, agent = agent, parent_ = tool_choice)
                print(answer)
                await agent.asend(answer)
                break
            else:
                answer = Answer(utterance_ = "I apologize, but I did not find an answer.", agent = agent, parent_ = thought)
                print(answer)
                await agent.asend(answer)
                break
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
            thought
            for thought in {tool_names}
            if thought not in tool_filter
        ] and
        STOPS_AT(THOUGHT, "\\n") and
        STOPS_AT(TOOL, "\\n") and
        {tool_conditions}
    '''
