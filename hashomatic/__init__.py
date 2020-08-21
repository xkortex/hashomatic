from collections.abc import Mapping, Iterable
from boltons.dictutils import FrozenDict
from .registry import marshaller_registry



def hasho(obj):
    """Hash almost anything!"""
    pass
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
