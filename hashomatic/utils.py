from importlib import import_module


def full_typename(o):
    """
    Get the fully-qualified name of object 'o'.
    Python makes no guarantees as to whether the __module__ special
    attribute is defined, so we take a more circumspect approach.
    Alas, the module name is explicitly excluded from __qualname__
    in Python 3.
    Args:
        o: any object

    Returns:
        full type name

    Example:
        >>> full_typename('foo')
        str
    Example:
        >>> from datetime import datetime
        >>> full_typename(datetime.now())
        datetime.datetime

    Example:
        >>> import pathlib
        >>> full_typename(pathlib.Path)
        pathlib.Path

    """
    if isinstance(o, type):
        module = o.__module__
        name = o.__name__
    else:
        module = o.__class__.__module__
        name = o.__class__.__name__

    if module is None or module == str.__class__.__module__:
        return name  # Avoid reporting __builtin__

    return module + "." + name


def full_typename_to_type(typename: str) -> type:
    """
    Return a class type based on the fully-qualified name
    Args:
        typename: fully-qualified type name, e.g. 'module.submod.classname'

    Returns:
        a `type` object

    Unfortunately, it seems xdoctest currently can't handle builtins import
    also, numpy is sort of a bad choice here because the type `ndarray` is not
    actually used to instantiate arrays
    Example:
        >>> import numpy
        >>> t = full_typename_to_type('numpy.ndarray')
        >>> t
        <class 'numpy.ndarray'>
        >>> assert t is numpy.ndarray

    """
    parts = typename.rsplit(".", 1)

    if len(parts) == 2:
        # load the module, will raise ImportError if module cannot be loaded
        module_name, class_name = parts
        m = import_module(module_name)
    else:
        class_name = parts[0]
        m = __builtins__

    # get the class, will raise AttributeError if class cannot be found
    return getattr(m, class_name)


def strip_unders(s):
    """Remove understores, if it is a string, otherwise pass unchanged. """
    if isinstance(s, str):
        return s.replace("_", "")
    return s
