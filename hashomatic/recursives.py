from collections.abc import Mapping, Iterable
from hashomatic.base import BaseEncoder, EncoderPrimitive
from boltons.dictutils import FrozenDict



def iterable_crystallize(obj: Iterable):
    pass


def mapping_crystallize(obj: Mapping):
    tmp = {}
    for k in sorted(obj):
        tmp[crystallize(k)] = crystallize(obj[k])

    return FrozenDict(tmp)


def crystallize(obj):
    """Convert any object with a registered Freezer into a hashable, immutable FrozenObj
    This is the central dispatch for resolving types
    """
    if isinstance(obj, Mapping):
        return mapping_crystallize
