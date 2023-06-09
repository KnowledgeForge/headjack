from typing import List

from headjack.models.utterance import Utterance


def add_source_to_utterances(utterances: List[Utterance], source: str) -> List[Utterance]:
    for utterance in utterances:
        utterance.source = utterance.source or source
    return utterances
