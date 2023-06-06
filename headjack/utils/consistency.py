from enum import Enum
from textwrap import dedent, indent  # noqa: F401
from typing import List, Tuple

import lmql

from headjack.models.utterance import Answer, Response, Utterance  # noqa: F401


class Consistency(Enum):
    OFF = "OFF"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @staticmethod
    def value(kind: "Consistency") -> Tuple[int, float]:
        return {"OFF": (1, 0.0), "LOW": (2, 0.5), "MEDIUM": (4, 0.6), "HIGH": (6, 0.7)}[str(kind)]


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
        convo = indent(dedent(responses[0].parent.convo()), ' '*4)
        responses = indent(dedent("\n".join(str(res) for res in responses)), ' '*4)
        """You will be presented with several responses to the following conversation:

        Conversation:

        {convo}

        Responses:
        """
        for letter, response in zip(ascii_letters[26:], responses):
            "{letter}:\n"
            response_str = indent(dedent(str(response)), " "*4)
            "{response_str}\n\n"
        response_options = list(ascii_letters[26:26+len(responses)])
        "Which of responses {response_options} best represents all of them: [LETTER]"
        response = responses[ascii_letters[26:26+len(responses)].index(LETTER)]
        if not isinstance(response, (Answer, Response)):
            return response
        "\nCould you provide a better response by aggregating more information from the other responses? Yes or No: [DO_ADDENDUM]"
        if DO_ADDENDUM =='Yes':
            "\nUsing only information from the provided responses, your response would be: [ADDENDUM]"
            response.utterance=ADDENDUM
        return response
    FROM
        "chatgpt"
    WHERE
        LETTER in ascii_letters[26:26+len(responses)] and
        DO_ADDENDUM in ['Yes', 'No']
    '''
