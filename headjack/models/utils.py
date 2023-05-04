from typing import Callable, Protocol, Type, TypeVar

T = TypeVar("T")


def required_value(message: str, return_type: Type[T]) -> Callable[[], T]:
    def raise_message() -> T:
        raise ValueError(message)

    return raise_message


class Stringable(Protocol):
    def __str__(self) -> str:
        pass

