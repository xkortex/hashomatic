from typing import TypeVar

Serializable = TypeVar('Serializable', dict, list, tuple, str, int, float, bool)
JsonTypes = (dict, list, tuple, str, int, float, bool, type(None))
JsonPrimitive = (str, int, float, bool, type(None))



