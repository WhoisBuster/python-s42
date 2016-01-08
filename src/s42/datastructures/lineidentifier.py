

class LineIdentifier(object):

    @classmethod
    def fromxml(cls, element):
        assert element.tag == 'lineName'
        return cls(element.get('lineNumber'), element.text)

    def __init__(self, numeric, symbolic):
        self._numeric = numeric
        self._symbolic = symbolic

    def __iter__(self):
        return iter([self._numeric, self._symbolic])

    def __hash__(self):
        return hash(tuple(self))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __repr__(self):
        return "<LineIdentifier: {0} ({1})>".format(
            self._numeric, repr(self._symbolic))
