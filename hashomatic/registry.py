from .datatypes import JsonTypes
from .base import NopFreezer, BaseFreezer

_default = object()


class MarshallerRegistry(dict):
    def __init__(self, **kwargs):
        self.nm = NopFreezer()
        kwargs.update(
            {"JsonTypes": self.nm, None: None}
        )  # None gives use default fallthrough behavior
        super(MarshallerRegistry, self).__init__(kwargs)

    def register(self, marshaller: BaseFreezer):
        # allow lookup by both type and name
        self.update({marshaller.type_: marshaller, marshaller.name: marshaller})

    def assert_type(self, obj):
        m = self.get(type(obj), None)
        if m is not None:
            return True

        assert m in JsonTypes, "Could not find marshaller for type {}".format(type(obj))

    def typenames(self):
        return [k for k in self.keys() if isinstance(k, str)]


marshaller_registry = MarshallerRegistry()
