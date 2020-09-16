from io import BytesIO
from collections.abc import Mapping, Iterable
from hashlib import md5
from hashomatic.utils import full_typename

hashf = md5
HASH_TYPE = type(hashf())


def stringer(a):
    """
    A way of string-ifying values such as "None" and "False" in a way that is unlikely to collide with the json
    text representation of that object
    :param a: any object
    :return: string representation which embeds both type and value

    Examples:
        >>> stringer(0)
        int(0)
        >>> stringer(None)
        NoneType(None)
        >>> stringer(False)
        bool(False)
    """
    return "{}({})".format(type(a).__name__, a)


class Hasher(object):
    """

    Example:
        >>> s = Hasher('hello world'.encode())
        >>> s.digest_size
        16
        >>> s.block_size
        64
        >>> s.msg.hexdigest()
        '5eb63bbbe01eeed093cb22bb8f5acdc3'
        >>> s.hexdigest()
        '5eb63bbbe01eeed093cb22bb8f5acdc3'
        >>> s.nonexistant()
        Traceback (most recent call last):
        ...
        AttributeError: '_hashlib.HASH' object has no attribute 'nonexistant'
        >>> s2 = s.copy()
        >>> s2.digest() == s.digest()
        True
        >>> s2.update("text".encode())
        >>> s2.digest() == s.digest()
        False

    Example:
        >>> s = Hasher('hello world'.encode())
        >>> s2 = Hasher(s)
        >>> s2.hexdigest()
        '5eb63bbbe01eeed093cb22bb8f5acdc3'
        >>> s is s2
        False
        >>> s.msg is s2.msg
        False


    """

    def __init__(self, data=None):
        if data is None:
            self.msg = hashf()
            return

        if isinstance(data, Hasher):
            self.msg = data.msg.copy()
            data = b""
        elif isinstance(data, HASH_TYPE):
            self.msg = data.copy()
            data = b""
        else:
            self.msg = hashf()
        self.msg.update(data)

    def __getattr__(self, key):
        return getattr(self.msg, key)

    def digest(self):
        return self.msg.digest()

    def hexdigest(self):
        return self.msg.hexdigest()

    def copy(self):
        result = Hasher()
        result.msg = self.msg.copy()
        return result

    def update(self, data):
        self.msg.update(data)

    def __add__(self, other):
        """Syntax sugar"""
        if not isinstance(other, Hasher):
            other = Hasher(other)

        self.update(other.digest())
        return self

    def __eq__(self, other):
        return self.msg.digest() == other.msg.digest()

    def __lt__(self, other):
        return self.msg.digest() <= other.msg.digest()

    def __gt__(self, other):
        return self.msg.digest() >= other.msg.digest()


    def __str__(self):
        return self.hexdigest()


def _lazyhash_dict(d: Mapping) -> Hasher:
    """

    :param d:
    :return:

    Examples:
        >>> str(_lazyhash_dict({'a': 2, 3: 3.14}))
        40f1f887b979c36cb94b3fafd56a4559
    """
    msg = Hasher(stringer(type(d)).encode())
    keyhashes = {str(lazyhash(k)): k for k in d}
    for khash in sorted(keyhashes):
        msg += lazyhash(khash)
        msg += lazyhash(d[keyhashes[khash]])
    return msg


def _lazyhash_iter(d: Iterable) -> Hasher:
    """

    :param d:
    :return:

    Examples:
        >>> str(_lazyhash_iter(['a', 2, b'd', 3.14]))
        e709c6b0e64138e6c5562da42dcacbdd
    """
    msg = Hasher(stringer(type(d)).encode())
    for k in d:
        msg += lazyhash(k)
    return msg


def _lazyhash_set(d: set) -> Hasher:
    """
    Sets are weird and tend to be non-deterministic when hashed
    :param d:
    :return:

    Examples:
        >>> s = {'a', 2, b'd', 3.14}
        >>> str(_lazyhash_set(s))
        33d81b6e6d000f16db5ecdcef30ca424
    """
    msg = Hasher(stringer(type(d)).encode())
    d2 = [lazyhash(x) for x in d]
    for k in sorted(d2):
        msg += lazyhash(k)
    return msg


def lazyhash(a) -> Hasher:
    """Hash dang near anything. Not guaranteed to be fast, accurate, or anything other than a best-effort hash

    todo: known bug with coercion of Nan/inf to null in json

    Examples:
        >>> str(lazyhash('a'))
        0cc175b9c0f1b6a831c399e269772661
        >>> str(lazyhash(0))
        4136793a3e2443479e791d8df9269102
        >>> str(lazyhash(0.0))
        75892eca87ec0bc4a601b857240324d0
        >>> str(lazyhash(None))
        d41d8cd98f00b204e9800998ecf8427e
        >>> str(lazyhash(False))
        c1c301efa8ce15f48a7313e9c2db6c9c

    Examples:
        >>> str(lazyhash(['a', 2, b'd', 3.14]))
        e709c6b0e64138e6c5562da42dcacbdd
        >>> str(lazyhash(('a', 2, b'd', 3.14)))
        cc60f60957db404383637797f6eb2720

        >>> str(lazyhash((('a', 2), (b'd', 3.14))))
        bd6b66cee8dad021f867f4d2da9b88bd

        >>> str(lazyhash({'a': 2, 3: 3.14, 'nest': {'list': [1, 2], 'dict': {2: 4}}}))
        76eb9aa821436d36fe1084cb124aa53d

    Examples:
        >>> s = {'a', 2, b'd', 3.14}
        >>> str(lazyhash(s))
        33d81b6e6d000f16db5ecdcef30ca424
        >>> str(_lazyhash_set(s))
        33d81b6e6d000f16db5ecdcef30ca424

    Examples:
        >>> import numpy as np
        >>> a = np.arange(5)
        >>> str(lazyhash(a))
        7abd5742dd8a47fae30e03e1a8d1da47

    Examples:
        >>> import pandas as pd
        >>> import math
        >>> a = pd.DataFrame({0: [1, 2], 'a': ['b', 'c'], 'c': [5.5, math.nan]})
        >>> str(lazyhash(a))
        17c639d0eb96da94c25d67fd575c7bbb
        >>> str(lazyhash(pd.Series([5.5, math.nan, math.inf])))
        96708b44a3ade335f962180d19e2c718
        >>> str(lazyhash(pd.Series([5.5, math.nan, -math.inf])))
        96708b44a3ade335f962180d19e2c718
        >>> str(lazyhash(pd.Series([5.5, math.nan, math.inf, -math.inf])))
        365538c44d40776f11d90b27a417a51d

    """
    if isinstance(a, HASH_TYPE):
        return Hasher(a)
    if isinstance(a, Hasher):
        return Hasher(a)

    if isinstance(a, str):
        return Hasher(a.encode())
    elif isinstance(a, bytes):
        return Hasher(a)
    elif isinstance(a, (int, float, bool)):
        s = "{}({})".format(full_typename(a), a)
        return Hasher(s.encode())

    elif isinstance(a, dict):
        return _lazyhash_dict(a)

    elif isinstance(a, (list, tuple)):
        return _lazyhash_iter(a)

    elif isinstance(a, set):
        return _lazyhash_set(a)

    typename = type(a).__name__
    if typename in ("ndarray", "matrix"):
        import numpy as np

        assert isinstance(a, (np.ndarray, np.matrix))
        b = BytesIO()
        np.save(b, a)
        return Hasher(b.getbuffer())
    elif typename in ("Series", "DataFrame"):
        import pandas as pd

        assert isinstance(a, (pd.Series, pd.DataFrame))
        if isinstance(a, pd.Series):
            df = a.to_frame()  ## yeah this is lazy, hence lazyhash
        else:
            df = a
        b = BytesIO()
        try:
            df.to_parquet(b)
            return Hasher(type(a).__name__.encode() + b.getbuffer())
        except ValueError:
            return Hasher(type(a).__name__.encode() + df.to_json().encode())

    elif isinstance(a, Mapping):
        return _lazyhash_dict(a)

    elif isinstance(a, Iterable):
        return _lazyhash_iter(a)

    # all out of ideas
    return Hasher(a)
