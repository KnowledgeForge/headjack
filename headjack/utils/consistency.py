from enum import Enum
from textwrap import dedent, indent  # noqa: F401
from typing import List

import lmql

from headjack.models.utterance import Answer, Response, Utterance  # noqa: F401


class Consistency(Enum):
    OFF = (1, 0.0)
    LOW = (2, 0.5)
    MED = (4, 0.6)
    HIGH = (6, 0.7)


async def consolidate_responses(responses: List[Utterance]) -> Utterance:
    if not all((responses[0].parent is res.parent for res in responses)):
        raise ValueError("Responses have different parents.")
    if len(responses) > 26:
        raise ValueError("Cannot have more than 26 responses.")
    if len(responses) == 1:
        return responses[0]
    return (await _consolidate_responses(responses))[0]


@lmql.query
async def _consolidate_responses(responses: List[Utterance]) -> List[Utterance]:  # type: ignore
    '''lmql
    argmax
        """You will be presented with several responses to the following conversation:

        Conversation:"""
        convo = indent(dedent(responses[0].parent.convo()), " "*4)
        responses = indent(dedent("\n".join(str(res) for res in responses), " "*4)
        """
        {convo}

        Responses:
        """
        for letter, response in zip(ascii_letters[26:], responses):
            "{letter}:\n"
            response_str = indent(dedent(str(response)), " "*4)
            "{response_str}\n\n"

        "Which of responses {list(ascii_letters[26:26+len(responses)])} best represents all of them: [LETTER]"
        response = responses[ascii_letters[26:26+len(responses)].index(LETTER)]
        if not isinstance(response, (Answer, Response)):
            return response
        "\nCould you provide a better response by aggregating more information from the other responses? Yes or No: [DO_ADDENDUM]"
        if DO_ADDENDUM =='Yes':
            "\nUsing only information from the provided responses, your response would be: [ADDENDUM]"
            response.utterance=ADDENDUM
        return response
    from
        chatgpt
    where
        LETTER in ascii_letters[26:26+len(responses)] and
        DO_ADDENDUM in ['Yes', 'No']
    '''
