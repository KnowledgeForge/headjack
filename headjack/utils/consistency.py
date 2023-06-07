from dataclasses import dataclass
from enum import Enum
from string import ascii_letters  # noqa: F401
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
    def map(kind: "Consistency") -> Tuple[int, float]:
        return {"OFF": (1, 0.0), "LOW": (2, 0.5), "MEDIUM": (4, 0.6), "HIGH": (6, 0.7)}[kind.value]


async def consolidate_responses(responses: List[Utterance]) -> Utterance:
    if not all((responses[0].parent.id == res.parent.id for res in responses)):
        raise ValueError("Responses have different parents.")
    if len(responses) > 26:
        raise ValueError("Cannot have more than 26 responses.")
    if len(responses) == 1:
        return responses[0]
    return (
        await _consolidate_responses(
            _ConsolidateResponsesArgs(list(ascii_letters[26 : (26 + len(responses))]), responses),  # noqa: E203
        )
    )[0]


@dataclass
class _ConsolidateResponsesArgs:
    choices: List[str]
    responses: List[Utterance]


@lmql.query
async def _consolidate_responses(args: _ConsolidateResponsesArgs) -> List[Utterance]:  # type: ignore
    '''lmql
    argmax
        convo = indent(dedent(args.responses[0].parent.convo()), ' '*4)
        responses = indent(dedent("\n".join(str(res) for res in args.responses)), ' '*4)
        """You will be presented with several responses to the following conversation:

        Conversation:

        {convo}

        Responses:
        """
        for letter, response in zip(ascii_letters[26:], args.responses):
            "{letter}:\n"
            response_str = indent(dedent(str(response)), " "*4)
            "{response_str}\n\n"
        "Which of responses {args.choices} best represents all of them: [LETTER]"
        response = args.responses[args.choices.index(LETTER)]
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
        LETTER in args.choices and
        DO_ADDENDUM in ['Yes', 'No']
    '''
