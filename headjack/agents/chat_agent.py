import asyncio
import logging
from dataclasses import dataclass
from textwrap import dedent, indent  # noqa: F401
from typing import Optional

import lmql

from headjack.agents.registry import AGENT_REGISTRY
from headjack.models.utterance import Action, Answer, Response, Utterance  # noqa: F401
from headjack.utils.add_source_to_utterances import add_source_to_utterances
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
    queue_index: int


async def chat_agent(
    question: Utterance,
    max_steps: int = 3,
    chat_consistency: Consistency = Consistency.OFF,
    agent_consistency: Consistency = Consistency.OFF,
) -> Utterance:
    n_async = Consistency.map(chat_consistency)[0]
    async_buffer = [[] for _ in range(max_steps)]
    working_index = 0
    queue = asyncio.Queue()
    chat_task = asyncio.create_task(
        _chat_agent(
            ChatAgentArgs(question, queue, max_steps, *Consistency.map(chat_consistency), *Consistency.map(agent_consistency)),
        ),
    )
    while True:
        response = await queue.get()
        async_buffer[response.queue_index].append(response.utterance)
        if len(async_buffer[working_index]) == n_async:
            if all((res is None for res in async_buffer[working_index])):  # all agent paths completed already
                yield None
                break
            fin = await consolidate_responses(  # otherwise rollup the utterances which were not None to a consensus or best utterance
                add_source_to_utterances(
                    [res for res in async_buffer[working_index] if res is not None],
                    "chat_agent",
                ),
            )
            yield fin
            working_index += 1
    chat_task.cancel()


@lmql.query
async def _chat_agent(args: ChatAgentArgs) -> lmql.LMQLResult:  # type: ignore
    '''lmql
    sample(n = args.n, temperature = args.temp, max_len=4096)
        """You are a chatbot that takes a conversation between you and a User and continues the conversation appropriately.

        DO NOT USE INFORMATION FROM THIS SECTION TO RESPOND TO THE USER ONLY USE IT TO HELP INFORM YOUR PLAN AND SPECIALIST CHOICE
            Example interaction:
            User: what are you capable of?/what can you help me with?/how can you help me?
            Plan: I will tell the user about my available agents. I do not need to dispatch any specialist to do this.
            Answer: I have access to several specialist agents...

            Example interaction:
            User: what is the total sales for the products
            Plan: The user has asked for something that sounds like a computable value and so I will dispatch the metric_calculate_agent.
            Action: ...

            Example interaction:
            User: is there any information about the company dj roads?
            Plan: I will check with the knowledge search agent, but there may be information in the user messages so I will clarify with the user if I should search messages as well.
            Response: Should I search the message system in addition to the knowledge repository?
            User: yes
            Action: ...uses knowledge search...
        END OF EXAMPLE INFORMATION TO IGNORE

        To aid you in responding to the user, you have access to several helpful specialist AI agents that can help with tasks or questions you dispatch to them.

        The specialists at your disposal to dispatch to are:
        {dispatchable_agents}

        Conversation:
        {dedent(args.question.convo(set((Observation,))))}

        """
        _logger.info(f"""
        CONVERSATION:
        {dedent(args.question.convo(set((Observation,))))}
        """)
        steps = -1
        while args.max_steps>steps:
            steps+=1
            """
            Describe a high-level plan to continue to respond to the user. You should be able to describe in less than 50 words.
            Plan: [PLAN]
            """
            _logger.info(PLAN)
            if steps>1:
                """
                Based on your plan and any additional information above, do you need to ask any clarifying questions? You will need to explain to the user why you are asking and how you will use the information to help them.
                Yes for clarifying information otherwise No.: [CLARIFY]
                """
                if CLARIFY=='Yes':
                    "Ask and explain your question as tersely as possible:"
                    "[CLARIFICATION]"

                    await args.queue.put(ChatRollupWrapper(Response(utterance=CLARIFICATION, parent=args.question), steps))
                    break
            """
            Based on your plan and any additional information above, do you need to dispatch a specialist to assist in your response?
            Yes for specialist otherwise No.: [SPECIALIST]
            """
            if SPECIALIST=='Yes':
                
                """
                In a few words, explain which specialists you thing would be best for this and why based on their descriptions.
                [REASONING]
                The agent that seems best suited to handle this part of your plan is: [AGENT]
                What is the question or task this specialist should assist you with?
                Write your request in the task xml tags below e.g. <task>your task description or question here</task>.
                Your request should be as terse as possible, most likely less than 100 words. 
                Be as plain in your task request/description as possible. Speak to them very plainly without courtesy.
                Do not add anything to your task request that is not derived from above.
                Be sure to include all the necessary information so long as it is from the above.
                <task>[TASK]task>
                """
                task = Action(utterance=TASK.strip('</'), parent=args.question)
                _logger.info(f"Chat agent dispatching to {AGENT} for task `{task}`.")
                result = (await AGENT_REGISTRY[AGENT][1](task, args.agent_n, args.agent_temp))
                """
                The {AGENT} completed the task. Did your plan necessitate using any further specialists? Yes or No: [SPECIALIST]
                """
                result_str = str(result)[:500]
                if SPECIALIST=='Yes':
                    "The {AGENT} gave this (shown here truncated to the first 500 chars)\n"
                    "{result_str}\n"
                    continue

                if result.direct_response:
                    await args.queue.put(ChatRollupWrapper(result, steps))
                    break
                "Is the result of this {AGENT} likely a response to the user? Yes or No.: [IS_DIRECT]"
                if IS_DIRECT=='Yes':
                    await args.queue.put(ChatRollupWrapper(result, steps))
                    break
                else:
                    "(result shown here truncated to the first 500 chars)\n"
                    "{result_str}\n"
                    "Seeing this part of the result, is it likely it should be a direct response to the user's message? Yes or No.: [IS_DIRECT]"
                    if IS_DIRECT=='Yes':
                        await args.queue.put(ChatRollupWrapper(result, steps))
                        break
            else:
                """Respond to the user in a few words (preferably less than 200) using information directly available to you in this conversation.
                Answer: [ANSWER]"""
                await args.queue.put(ChatRollupWrapper(Answer(utterance=ANSWER, parent=args.question), steps))
                break
        for i in range(1+args.max_steps-steps):
            await args.queue.put(ChatRollupWrapper(None, steps+1+i))
    from
        "chatgpt"
    where
        AGENT in [agent for agent in AGENT_REGISTRY.keys()] and
        SPECIALIST in ['Yes', 'No'] and
        CLARIFY in ['Yes', 'No'] and
        STOPS_AT(TASK, '</')
    '''
