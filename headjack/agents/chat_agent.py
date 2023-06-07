import logging
from dataclasses import dataclass
from textwrap import dedent, indent  # noqa: F401

import lmql

from headjack.agents.registry import AGENT_REGISTRY
from headjack.models.utterance import Action, Answer, Utterance  # noqa: F401
from headjack.utils.consistency import Consistency  # noqa: F401

_logger = logging.getLogger("uvicorn")


dispatchable_agents = indent(
    dedent("\n".join([f"{agent_name}: {agent_description}" for agent_name, (agent_description, _) in AGENT_REGISTRY.items()])),
    " " * 4,
)


async def chat_agent(
    question: Utterance,
    max_steps: int = 3,
    chat_consistency: Consistency = Consistency.OFF,
    agent_consistency: Consistency = Consistency.OFF,
) -> Utterance:
    return await _chat_agent(
        ChatAgentArgs(question, max_steps, *Consistency.map(chat_consistency), *Consistency.map(agent_consistency)),
    )


@dataclass
class ChatAgentArgs:
    question: Utterance
    max_steps: int
    n: int
    temp: float
    agent_n: int
    agent_temp: float


@lmql.query
async def _chat_agent(args: ChatAgentArgs) -> Utterance:  # type: ignore
    '''lmql
    sample(n = n, temperature = temp)
        """You are an chatbot that takes a conversation between you and a User and continues the conversation appropriately.
        To aid you in responding to the user, you have access to several helpful specialist agents that can help with tasks or questions you dispatch to them.

        The specialists at your disposal to dispatch to are:
        {dispatchable_agents}

        Conversation:
        {dedent(args.question.convo())}
        """
        steps = 0
        while args.max_steps>steps:
            "Is there information available in the existing conversation that can be used to respond? Yes or No.: [CONVO_INFO]\n"
            if CONVO_INFO=='No':
                """Do you need help from a specialist to continue or can you respond immediately based on information from the existing conversation?
                Yes for specialist otherwise No.: [SPECIALIST]
                """
            if CONVO_INFO=='No' and SPECIALIST=='Yes':
                steps+=1
                """The agent that seems best suited to handle this request is: [AGENT]
                What is the question or task this specialist should assist you with?
                Write your request in the task xml tags below e.g. <task>your task description or question here</task>. Your request should be as terse as possible, most likely less than 100 words.
                <task>[TASK]task>
                """
                task = Action(utterance=TASK.strip('</'), parent_=args.question)
                _logger.info(f"Chat agent dispatching to {AGENT} for task `{task}`.")
                result = (await AGENT_REGISTRY[AGENT][1](task, args.agent_n, args.agent_temp))
                "Is the result of this specialist likely a response to the user? Yes or No.: [IS_DIRECT]"
                if IS_DIRECT=='Yes':
                    return result
                else:
                    "{result}\n"
                    "Seeing the result, is it likely it constitutes a direct response to the user? Yes or No.: [IS_DIRECT]"
                    if IS_DIRECT=='Yes':
                        return result
            else:
                """Respond to the user in a few words (less than 200) using information directly available to you in this conversation.
                Answer: [ANSWER]"""
                return Answer(utterance=ANSWER, parent_=args.question)
    from
        "chatgpt"
    where
        AGENT in [agent for agent in AGENT_REGISTRY.keys()] and
        SPECIALIST in ['Yes', 'No'] and
        CONVO_INFO in ['Yes', 'No'] and
        SPECIALIST in ['Yes', 'No'] and
        CONVO_INFO in ['Yes', 'No'] and
        IS_DIRECT in ['Yes', 'No'] and
        STOPS_AT(TASK, '</') and
        STOPS_AT(ANSWER, '\n')
    '''
