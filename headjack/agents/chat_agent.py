import logging
from textwrap import dedent, indent  # noqa: F401

import lmql

from headjack.agents.registry import AGENT_REGISTRY
from headjack.models.utterance import Utterance

_logger = logging.getLogger("uvicorn")


dispatchable_agents = indent(
    dedent("\n".join([f"{agent_name}: {agent_description}" for agent_name, (agent_description, _) in AGENT_REGISTRY.items()])),
    " " * 4,
)


@lmql.query
async def chat_agent(question: Utterance) -> Utterance:  # type: ignore
    '''lmql
    argmax
        """You are an chatbot that takes a conversation between you and a User and continues the conversation appropriately.
        To aid you in responding to the user, you have access to several helpful specialist agents that can answer questions you dispatch to them.

        The specialists at your disposal to dispatch to are:
            {dispatchable_agents}

        {question.convo()}
        
        Do you need help from a specialist to answer this request? Yes or No.: [YESNO]
        """
        if YESNO=='Yes':
            """The agent that seems best suited to handle this request is: [AGENT]
            What is the question or task this specialist should assist you with?
            Write your request in the task xml tags below e.g. <task>your task description or question here</task>. Your request should be as terse as possible, most likely less than 100 words.
            <task>[TASK]task>
            """
            task = Action(utterance=TASK.strip('</'), parent_=question)
            _logger.info(f"Dispatching to {AGENT} for agent defined task request `{task}`.")
            return await AGENT_REGISTRY[AGENT][1](task)
        else:
            """Respond to the user in a few words (less than 200) using information directly available to you in this conversation.
            Answer: [ANSWER]"""
    from
        "chatgpt"
    where
        AGENT in [agent for agent in AGENT_REGISTRY.keys()] and
        YESNO in ['Yes', 'No'] and
        STOPS_AT(TASK, '</') and 
        STOPS_AT(ANSWER, '\n')
    '''
