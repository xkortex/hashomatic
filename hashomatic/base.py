import json
from collections.abc import Iterable, Mapping
from abc import abstractmethod
from typing import TypeVar, Generic
from hashomatic.utils import full_typename
from hashomatic.datatypes import Serializable, JsonPrimitive

T = TypeVar("T")


class DefaultEncodable(object):
    ...


class BaseEncoder(object):
    """Base class for objects that can be encoded to bytes
    """

    subclasses = {}
    type_ = DefaultEncodable  # type T the marshaller handles
    name = full_typename(type_)  # fully-qualified name of type T the marshaller handles

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.update({cls.name: cls})

    def encode(self, *args, **kwargs) -> bytes:
        """
        Convert an object of type T into bytes
        By default, it will just try to call "encode" on it.

        Args:
            obj: some object of type T

        Returns:
            some binary encoding of obj
        """
        if getattr(self, "decode", None):
            assert isinstance(self, bytes)
            return self  # is already encoded

        encode = getattr(self, "encode", None)
        if encode:
            b = self.encode(*args, **kwargs)
            assert isinstance(b, bytes)
            return b
        raise NotImplementedError(
            "Type {} does not implement `encode`".format(type(self))
        )


class BaseFreezer(object):
    """Base class for the freeze interface mixin.
    A Freezer should implement freeze(), which takes a T and returns an immutable, hashable object,
    and __hash__(), which is the python hash default method

    todo: do something clever to reduce the boilerplate and set up the type hints
    """

    subclasses = []

    type_ = object  # type T the marshaller handles

    name = full_typename(type_)  # fully-qualified name of type T the marshaller handles

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    # todo: we want to enforce something having __hash__, but do not want to override it if it exists. i think this is the way
    @abstractmethod
    def __hash__(self):
        ...

    @abstractmethod
    def freeze(self):
        ...


class NopFreezer(BaseFreezer):
    type_ = Serializable
    name = "Serializable"
    # we just pass it straight through


class FrozenIterable(Iterable, BaseFreezer):
    @classmethod
    def freeze(cls, obj):
        return tuple(obj)  # todo: add recursion

    def __hash__(self):
        return hash(FrozenIterable.freeze(self))


class EncoderPrimitive(BaseEncoder):
    def encode(self, *args, **kwargs) -> bytes:
        """
        """
        return json.dumps(self).encode()


class EncoderInt(int, EncoderPrimitive):
    type_ = int
    name = "int"


class EncoderFloat(float, EncoderPrimitive):
    type_ = float
    name = "float"


class FreezablePrimitive(BaseFreezer):
    def freeze(self, *args, **kwargs) -> bytes:
        """
        """
        return self

