from base64 import urlsafe_b64encode
import json
from collections.abc import Iterable, Mapping
from abc import abstractmethod
from typing import cast
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

    @classmethod
    @abstractmethod
    def crystallize(cls, obj):
        ...


class Crystal(dict, BaseCrystal):
    """A Crystal is an immutable mapping
    A Crystal should implement freeze(), which takes a T and returns an immutable, hashable object,
    and __hash__(), which is the python hash default method

    """

    subclasses = {}
    type_ = dict  # type T the marshaller handles
    name = full_typename(type_)  # fully-qualified name of type T the marshaller handles

    def __hash__(self):
        tmp = CrystalTuple(((hash(k), hash(v)) for k, v in self.items()))
        return hash(tmp)

    def freeze(self):
        ...

    @classmethod
    def crystallize(cls, d: Mapping):
        """
        Initialize from a mapping-like object.
        Can also be used to capture Namespace or objects with __dict__ by calling
        crystallize(vars(ns))
        Args:
            d: dict/mapping with .items() method

        Returns:
            Crystal with copied fields

        Example:
            >>> x = FooCrystal.crystallize({'foo': 2, 'bar': 3})
            >>> x
            FooCrystal(foo=2, bar=3)
            >>> type(x).__name__
            FooCrystal
            >>> FooCrystal.crystallize({'bar': 3})
            FooCrystal(bar=3)
            >>> SpamCrystal(foo=2).copy()
            SpamCrystal(foo=2)

        Example:
            >>> from argparse import Namespace
            >>> ns = Namespace(foo=2, bar=3)
            >>> FooCrystal.crystallize(vars(ns))
            FooCrystal(foo=2, bar=3)
        """
        tmp = cls.__new__(cls)  # we need a totally blank object
        for key, value in d.items():
            tmp[key] = value
        return tmp

    def copy(self):
        """
        Shallow copy of this object
        Returns:
            New instance of this object with the same fields

        Examples
        Examples:
            >>> x = FooCrystal.crystallize({'foo': 2, 'bar': 3})
            >>> y = x.copy()
            >>> x == y
            True
            >>> x is y
            False
            >>> x['foo'] is y['foo']
            True
            >>> del x
            >>> y['foo']
            2
        """
        return self.__class__.crystallize(self)


class CrystalTuple(tuple, BaseCrystal):
    """A CrystalList is like a tuple, but applies recursively

    """

    subclasses = {}
    type_ = dict  # type T the marshaller handles
    name = full_typename(type_)  # fully-qualified name of type T the marshaller handles

    def __new__(cls, iterable=()):
        return tuple.__new__(CrystalTuple, (crystallize(x) for x in iterable))

    def freeze(self):
        ...

    @classmethod
    def crystallize(cls, iterable: Iterable):
        return tuple.__new__(CrystalTuple, (crystallize(x) for x in iterable))

    def copy(self):
        """
        Shallow copy of this object
        Returns:
            New instance of this object with the same fields

        Examples
        Examples:
            >>> x = FooCrystal.crystallize({'foo': 2, 'bar': 3})
            >>> y = x.copy()
            >>> x == y
            True
            >>> x is y
            False
            >>> x['foo'] is y['foo']
            True
            >>> del x
            >>> y['foo']
            2
        """
        return self.__class__(self)


class CrystalSet(frozenset, BaseCrystal):
    """A CrystalSet is like a frozenset, but applies recursively

    """

    subclasses = {}
    type_ = set  # type T the marshaller handles
    name = full_typename(type_)  # fully-qualified name of type T the marshaller handles

    def __new__(cls, s: Iterable = ()):
        return cast(CrystalSet, super().__new__(cls, s))

    def freeze(self):
        ...

    @classmethod
    def crystallize(cls, s: Iterable = ()):
        return cast(CrystalSet, super().__new__(cls, s))

    def copy(self):
        """
        Shallow copy of this object
        Returns:
            New instance of this object with the same fields

        """
        return self.__class__(self)


class CrystalBytes(bytes, BaseCrystal):
    """like bytes, but json-encodable

    """

    subclasses = {}
    type_ = bytes  # type T the marshaller handles
    name = full_typename(type_)  # fully-qualified name of type T the marshaller handles

    def __new__(cls, b: bytes = b""):
        return cast(CrystalBytes, super().__new__(cls, b))

    def __str__(self):
        return urlsafe_b64encode(self)

    def freeze(self):
        return self

    @classmethod
    def crystallize(cls, b: bytes):
        return bytes.__new__(b)


def mapping_crystallize(obj: Mapping):
    tmp = {}
    # todo: sorting is currently unstable due to heterogeneous types
    for k in sorted(obj):
        tmp[crystallize(k)] = crystallize(obj[k])

    return Crystal(tmp)


def crystallize(obj):
    """Convert any object with a registered Freezer into a hashable, immutable FrozenObj
    This is the central dispatch for resolving types
    """

    if isinstance(obj, JsonPrimitive):
        return obj

    if isinstance(obj, Mapping):
        return mapping_crystallize(obj)

    if isinstance(obj, bytes):
        return CrystalBytes(obj)

    if isinstance(obj, Iterable):
        return CrystalTuple(obj)

    raise NotImplemented("cannot handle type: {}".format(type(obj)))


class FooCrystal(Crystal):
    """For testing"""

    __slots__ = ["foo", "bar"]


class SpamCrystal(Crystal):
    """For testing. Has mandatory fields"""

    __slots__ = ["foo", "bar", "spam"]

    def __init__(self, foo, bar=None, spam=None):
        tmp = {
            k: v for k, v in locals().items() if v is not None and k in self.__slots__
        }
        super(SpamCrystal, self).__init__(**tmp)
