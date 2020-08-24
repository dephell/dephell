# built-in
from typing import Any, Callable, Generic, Optional, Type, TypeVar, overload


_AnyCallable = Callable[..., Any]

_T = TypeVar("_T")
_S = TypeVar("_S")


# https://github.com/python/typeshed/blob/master/stdlib/3/functools.pyi
class cached_property(Generic[_S, _T]):
    func: Callable[[_S], _T]

    def __init__(self, func: Callable[[_S], _T]) -> None:
        ...

    @overload
    def __get__(self, instance: None, owner: Optional[Type[_S]] = ...) -> 'cached_property[_S, _T]':
        ...

    @overload
    def __get__(self, instance: _S, owner: Optional[Type[_S]] = ...) -> _T:
        ...

    def __set_name__(self, owner: Type[_S], name: str) -> None:
        ...
