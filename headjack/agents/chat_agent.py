import asyncio
import logging
from dataclasses import dataclass
from textwrap import dedent, indent  # noqa: F401
from typing import AsyncGenerator, Dict, List, Optional, cast
from uuid import UUID, uuid4  # noqa: F401

import lmql
from lmql.runtime.bopenai import get_stats
from headjack.agents.registry import AGENT_REGISTRY
from headjack.models.utterance import (  # noqa: F401
    Action,
    Answer,
    Response,
    Thought,
    Utterance,
)
from headjack.utils.add_source_to_utterances import add_source_to_utterances
from headjack.utils.basic import strip_whole  # noqa: F401
from headjack.utils.consistency import Consistency, consolidate_responses

_logger = logging.getLogger("uvicorn")


dispatchable_agents = indent(
    dedent("\n".join([f"{agent_name}: {agent_description}" for agent_name, (agent_description, _) in AGENT_REGISTRY.items()])),
    " " * 4,
)


@dataclass
class ChatAgentArgs:
    question: Utterance
    queue: asyncio.Queue
    max_steps: int
    n: int
    temp: float
    agent_n: int
    agent_temp: float


@dataclass
class ChatRollupWrapper:
    utterance: Optional[Utterance]
    agent_id: UUID


async def chat_agent(
    question: Utterance,
    max_steps: int = 5,
    chat_consistency: Consistency = Consistency.OFF,
    agent_consistency: Consistency = Consistency.OFF,
) -> AsyncGenerator[Optional[Utterance], None]:
    n_async = Consistency.map(chat_consistency)[0]
    async_buffer: Dict[UUID, List[Utterance]] = {}
    working_index = 0
    queue: asyncio.Queue[ChatRollupWrapper] = asyncio.Queue()
    asyncio.create_task(
        _chat_agent(
            ChatAgentArgs(question, queue, max_steps, *Consistency.map(chat_consistency), *Consistency.map(agent_consistency)),
        ),
    )

    while True:
        response = await queue.get()
        if response.agent_id is None:
            yield response.utterance
            continue
        async_buffer[response.agent_id] = async_buffer.get(response.agent_id, []) + [cast(Utterance, response.utterance)]
        temp = []
        for utterance_list in async_buffer.values():
            if working_index >= len(utterance_list):
                break
            temp.append(utterance_list[working_index])
        if len(temp) != n_async:
            continue

        if all((res is None for res in temp)):  # all agent paths completed already
            yield None
            break

        fin = await consolidate_responses(  # otherwise rollup the utterances which were not None to a consensus or best utterance
            add_source_to_utterances(
                [res if res is not None else Response(utterance="None") for res in temp],
                "chat_agent",
            ),
        )

        yield fin
        working_index += 1
    _logger.info(get_stats())


@lmql.query
async def _chat_agent(args: ChatAgentArgs) -> lmql.LMQLResult:  # type: ignore
    '''lmql
    sample(n = args.n, temperature = args.temp, max_len=4096)
        """You are to play a chatbot named HeadJack that takes a conversation between you and a User and continues the conversation appropriately.

        # DO NOT USE INFORMATION FROM THIS SECTION TO RESPOND TO THE USER ONLY USE IT TO HELP INFORM YOUR PLAN AND SPECIALIST CHOICE
        #    Example interaction:
        #    User: what are you capable of?/what can you help me with?/how can you help me?
        #    Plan: I will tell the user about my available agents. I do not need to dispatch any specialist to do this.
        #    Answer: I have access to several specialist agents including (agent)____(/agent)...
        #
        #    Example interaction:
        #    User: what is the total sales for the products
        #    Plan: The user has asked for something that sounds like a computable value and so I will dispatch the (agent)metric_calculate_agent(/agent).
        #    Action: ...
        #
        #    Example interaction:
        #    User: Find the average repair cost by company and then plot it with a bar plot with red and pink.
        #    Plan: The (agent)metric_calculate_agent(/agent) will calculate the average repair cost by company and then the (agent)plot_data_agent(/agent) will make a bar plot with red and pink bars.
        #    Action: ...
        #
        #    Example interaction:
        #    ...
        #    User: make a bar chart of the data
        #    Plan: Looking in the conversation history, I can see I have previously dispatched an agent that calculates things. I will dispatch (agent)plot_data_agent(/agent) who will handle discovering the actual data from earlier in the conversation perform the plotting on its own.
        #    Action: ...
        #
        #    Example interaction:
        #    User: is there any information about the company dj roads?
        #    Plan: I will check with the knowledge search agent, but there may be information in the user messages so I will clarify with the user if I should search messages as well.
        #    Response: Should I search the message system in addition to the knowledge repository?
        #    User: yes
        #    Action: ...uses knowledge search...
        #END OF EXAMPLE INFORMATION TO IGNORE

        To aid you in responding to the user, you have access to several helpful specialist AI agents that can help with tasks or questions you dispatch to them.
        The specialists at your disposal are the following. Use them EXACTLY as their descriptions direct.:
        {dispatchable_agents}

        If a specialist is unable to complete a task at any time, consider whether to stop or simply report the issue to the user.
        If you ever refer to a specialist agent in a message for the user put it in tags like this: (agent)some_agent(/agent).


        Official Conversation:
        """
        convo = dedent(args.question.convo())
        """
        {convo}
        """
        _logger.info(f"""
        CONVERSATION:
        {convo}
        """)
        agent_id = uuid4()
        steps = -1
        parent = args.question
        while args.max_steps>steps:
            steps+=1
            """
            Consider the official conversation history, the latest user message, and the specialists at your disposal.
            Explain the user message and describe a high-level plan on how to formulate a response to the user.
            If the user is asking a question or telling you to do something and you cannot directly answer the user from the information already above you MUST use at least one specialist.
            You should be able to describe in less than 200 words and describe the order of all agents you will use.
            Only describe the agents you will use if you will use them to respond now.
            Only plan for tasks necessary to respond to what is explicitly requested by the user UNLESS a task is required to to be completed to get to tasks that will ultimately fulfill the user's request.
            If you plan to use specialists, ensure they are the most specifically dedicated to fulfilling the user's request and the narrowest set of agents possible that can accomplish all tasks.
            Do not use irrelevant specialists. Follow the agent descriptions exactly. You MUST explain what in the descriptions suggests their usage and contrast with a plan using a more limited set of specialists.
            Using a specialist that is not suited to your task is a critical mistake that can result in catastrophic consequences.
            Put your plan in plan tags `<plan>your plan</plan>
            <plan>[PLAN]plan>
            """
            _logger.info(PLAN)

            """
            Does your plan call for using a specialist? Yes or No.: [SPECIALIST]
            """
            if SPECIALIST=='Yes':
                """
                In a few words, explain which specialists you think would be best for this and why based on their descriptions.
                Put your reasoning in reasoning tags `<logic>your reasoning</logic>
                <logic>[REASONING]logic>

                In a few words, explain what you are doing now and why. Keep it short and sweet.
                Speak directly to the user using general terms. Do not ask questions now.
                If you refer to a specialist agent put it in tags for example (agent)chosen agent(/agent).
                Put your response in response tags `<logic>your logic response directly to the user</logic>
                <logic>[USER_REASONING]logic>"""
                _logger.info(REASONING)
                thought = Thought(utterance=strip_whole(USER_REASONING, '</'), parent=parent)
                await args.queue.put(ChatRollupWrapper(thought, agent_id))
                parent = thought
                """
                The agent that seems best suited to handle this part of your plan is: [AGENT]
                What is the question or task this specialist should assist you with?
                Write your request in the task xml tags below e.g. <task>your task description or question here</task>.
                Your request should be as terse as possible, most likely less than 100 words.
                Be as plain in your task request/description as possible. Speak to them very plainly without courtesy.
                Do not add anything to your task request that is not derived from above.
                Be sure to include all the necessary information so long as it is from the above.
                <task>[TASK]
                """
                task = Action(utterance=strip_whole(TASK, '</'), parent=parent)
                parent = task
                _logger.info(f"Chat agent dispatching to {AGENT} for task `{task}`.")
                result = (await AGENT_REGISTRY[AGENT][1](task, args.agent_n, args.agent_temp))
                parent = result
                await args.queue.put(ChatRollupWrapper(result, agent_id))
                "The {AGENT} responded with the following\n"
                "{result}\n\n"
                "In a few words, explain how this reponse does or does not contribute to fulfilling your plan and whether you believe it changes your plan. [EXPLAIN]\n"
                "With this explanation in mind, do you need to dispatch to more specialists to complete your latest plan? Yes or No. [CONTINUE]\n"
                if CONTINUE=='No':
                    break
            else:
                """Respond to the user in a few words (preferably less than 200) using information directly available to you in this conversation. Avoid repetition except to summarize.
                Answer: [ANSWER]"""
                answer = Answer(utterance=ANSWER, parent=parent)
                await args.queue.put(ChatRollupWrapper(answer, agent_id))
                break
        for i in range(100):
            await args.queue.put(ChatRollupWrapper(None, agent_id))
        "{uuid4()}"
    from
        "chatgpt"
    where
        AGENT in [agent for agent in AGENT_REGISTRY.keys()] and
        SPECIALIST in ['Yes', 'No'] and
        CONTINUE in ['Yes', 'No'] and
        STOPS_AT(TASK, '</') and
        STOPS_AT(PLAN, '</') and
        STOPS_AT(REASONING, '</') and
        STOPS_AT(USER_REASONING, '</')
    '''
