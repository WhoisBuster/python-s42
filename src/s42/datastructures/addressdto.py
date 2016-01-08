from s42.datastructures.code import Code


class AddressDTO(object):

    @classmethod
    def fromdict(cls, dto):
        return cls(dto)

    def __init__(self, elements):
        self._elements = {}
        for code, value in elements.items():
            code = Code.fromstring(code)
            self._elements[code] = value

        self._keys = set(self._elements.keys())

    def get(self, code):
        """Get the value of an address element by its code."""
        if isinstance(code, str):
            code = Code.fromstring(code)
        return self._elements.get(code)\
            or self._elements.get(code.base)

    def is_populated(self, code):
        """Return a boolean indicating if the specified element has a
        value.
        """
        if isinstance(code, str):
            code = Code.fromstring(code)
        return bool(set([code, code.base]) & self._keys)
