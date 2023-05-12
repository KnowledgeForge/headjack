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
        You are a chatbot Agent that helps users answer questions in a conversational way.
        Your answers are clear, concise and complete. Information you use after being provided an Observation should be about the Observation.
        You NEVER use marker phrases like User:, Thought:, Observation:, Action:, Answer: as these are used by the system.
        If the user asks for historical information about the conversation, you do not need to use tools and you must use the past Conversation provided and any Memory if provided. In other words, you may answer the user now by summarizing information from the conversation or history.
        If the user makes trivial or conversation that is outside the scope of your tools, inform the user of this.
        If the user is inquiring about your capabilities tell them what tools you have and their descriptions in your own terse summary.
        Anything the you the Agent says is based entirely on provable contextual information. The agent would be able to cite any information it provides. As such, the agent defers to tools if there is not information below to answer the user.

        Here are some snippets of example conversations where the agent uses thoughful reasoning. No information from these snippets should be used in replies to the User:
            User: the user asks a particular question
            Thought: I should use a tool.
            Tool: agent selects appropriate tool
            Action: 
                ___Here there will be multiple pieces of information that require you the Agent to fill in__
                name of field (description of field):
                __Possible need to select a number of items or determine whether this information is needed__
                Your chosen value or values for the field
            Observation: the tool will run with your inputs and some information that may contain all or part of an answer or response to the user will be an observation.
            ...
            User: my name is Joe
            Thought: This is trivial or irrelevant.
            Answer: Hello Joe! I am an assistant that can help you to solve problems. Feel free to inquire about my capabilities.
            User: What can you do?
            Thought: This is a question about my capabilities.
            Response: I have access to the following tools that can be used to...
            ...


        Here are the tools you may choose from:
{tools_prompt}

        """
        if utterance.parent:
            """
            
        Conversation History:
        {{utterance.parent.convo(history_length-1, history_utterances)}}
        
            """

        """
        
        Latest Conversation:
        {{utterance}}
        
        
        """

        # "Come up with a short problem description and plan for what the user has said.\\n"
        # "Problem: [PROBLEM]\\n"
        # problem = Thought(utterance_ = PROBLEM, agent = agent, parent_ = utterance)
        # await agent.asend(problem)
        # "Plan: [PLAN]\\n"
        # plan = Thought(utterance_ = PLAN, agent = agent, parent_ = problem)
        # await agent.asend(plan)
        parent_utterance = utterance
        for _ in range(loop_limit):
            "Thought: [THOUGHT]\\n"
            thought = Thought(utterance_ = THOUGHT, agent = agent, parent_ = parent_utterance)
            parent_utterance = thought
            await agent.asend(thought)
            retry_tool = False
            tool_choice = None
            if retry_tool or 'use a tool' in THOUGHT:
                tool_payloads=dict()
                "Tool: [TOOL]\\n"
                tool_choice = Thought(utterance_ = "I will use my "+TOOL, agent = agent, parent_=parent_utterance)
                parent_utterance = tool_choice
                await agent.asend(tool_choice)
                # import pdb; pdb.set_trace()
                {tool_body}
            elif 'answer the user' in THOUGHT:
                "Agent NEVER uses marker phrases like User:, Thought:, Observation:, Action:, Answer: as these are used by the system. "
                "Answers are concise and at most 200 words unless content is verbatim from observations.\\n"
                "Answer: [ANSWER]\\n"
                answer = Answer(utterance_ = ANSWER, agent = agent, parent_ = parent_utterance)
                await agent.asend(answer)
                break
            elif ('can do' in THOUGHT) or ('trivial' in THOUGHT):
                "This is something I can respond to the user directly or explain the irrelevance to the user without using tools.\\n"
                "Response: [ANSWER]\\n"
                answer = Answer(utterance_ = ANSWER, agent = agent, parent_ = parent_utterance)
                await agent.asend(answer)
                break
            elif 'help' in THOUGHT:
                "I need help determining what to do. I will explaing this to the user and tell them the tools I have access to so they can help me.\\n"
                "Answer: [ANSWER]\\n"
                answer = Answer(utterance_ = ANSWER, agent = agent, parent_ = parent_utterance)
                await agent.asend(answer)
                break
            else:
                answer = Answer(utterance_ = "I apologize, but I did not find an answer.", agent = agent, parent_ = parent_utterance)
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
                    "I need help deciding if I should use one of my tools?",
                    'I can answer the user now with information from the conversation.',
                    'I can answer the user now by extracting information from the memory.',
                    'I can answer the user now based on this latest information.',
                    # 'This is trivial or irrelevant.',
                    # "The user would like to know what I can do.",
                    "Some tools have tried and an answer could not be found yet."
                ]
            if thought not in thought_filter
        ] and
        TOOL in [
            tool
            for tool in {tool_names}
            if tool not in tool_filter
        ] and
        len(ANSWER)<500 and
        STOPS_AT(ANSWER, 'User') and STOPS_AT(ANSWER, 'Tool:') and STOPS_AT(ANSWER, 'Observ') and STOPS_AT(ANSWER, 'Answer') and 
        STOPS_AT(THOUGHT, "\\n") and
        STOPS_AT(TOOL, "\\n") and
        # STOPS_AT(PROBLEM, "\\n") and
        # STOPS_AT(PLAN, "\\n") and
        {tool_conditions}
    '''
