"""a registry of all agent functions"""

from typing import Any, Callable, Dict, Optional, Tuple

from headjack.models.utterance import Utterance

AGENT_REGISTRY: Dict[str, Tuple[str, Callable[[Utterance], Utterance]]] = {}


def register_agent_function(description: str, name: Optional[str] = None):
    def decorator(func: Callable[[Utterance], Any]):
        AGENT_REGISTRY[name or func.__name__] = (description, func)
        return func

    return decorator
