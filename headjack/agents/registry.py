"""a registry of all agent functions"""

from typing import Callable, Dict, Optional, Tuple, Any

AGENT_REGISTRY:Dict[str, Tuple[str, Callable[[str], Any]]]={}

def register_agent_function(description: str, name: Optional[str] = None):
    def decorator(f: Callable[[str], Any]):
        AGENT_REGISTRY[name or f.__name__]=(description, f)
        return f
    return decorator