from typing import List
from string importascii_letters,  ascii_letters
import lmql
from textwrap import indent, dedent # noqa: F401
from headjack.models.utterance import Utterance

async def consolidate_responses(responses: List[Utterance])-> Utterance:
    if not all((responses[0].parent is res.parent for res in responses)):
        raise ValueError("Responses have different parents.")
    return await _consolidate_responses(responses)
    
@lmql.query
async def _consolidate_responses(responses: List[Utterance])->Utterance:
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
    from
        chatgpt
    where
        LETTER in ascii_letters[26:26+len(responses)]
    '''