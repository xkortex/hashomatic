import json
from collections.abc import Iterable, Mapping
from abc import abstractmethod
from typing import TypeVar, Generic
from hashomatic.utils import full_typename
from hashomatic.datatypes import Serializable, JsonPrimitive

class DefaultCrystallizable(object):
    ...


class BaseCrystal(object):
    """A Crystal is an immutable object
    A Crystal should implement freeze(), which takes a T and returns an immutable, hashable object,
    and __hash__(), which is the python hash default method

    """
    subclasses = {}
    type_ = DefaultCrystallizable  # type T the marshaller handles
    name = full_typename(type_)  # fully-qualified name of type T the marshaller handles

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.update({cls.name: cls})

    # todo: we want to enforce something having __hash__, but do not want to override it if it exists. i think this is the way
    @abstractmethod
    def __hash__(self):
        ...

    @abstractmethod
    def freeze(self):
        ...


class CrystalDict(dict, BaseCrystal):
    """A CrystalDict is an immutable mapping
    A Crystal should implement freeze(), which takes a T and returns an immutable, hashable object,
    and __hash__(), which is the python hash default method

    """
    subclasses = {}
    type_ = dict  # type T the marshaller handles
    name = full_typename(type_)  # fully-qualified name of type T the marshaller handles

    @abstractmethod
    def __hash__(self):
        ...

    @abstractmethod
    def freeze(self):
        ...