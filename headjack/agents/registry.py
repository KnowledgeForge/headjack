"""a registry of all agent functions"""

from typing import Any, Callable, Dict, Optional, Tuple

from headjack.models.utterance import User, Utterance

AGENT_REGISTRY: Dict[str, Tuple[str, Callable[[User], Utterance]]] = {}


def register_agent_function(description: str, name: Optional[str] = None):
    def decorator(f: Callable[[User], Any]):
        AGENT_REGISTRY[name or f.__name__] = (description, f)
        return f

    return decorator
