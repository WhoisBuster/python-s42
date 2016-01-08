from s42.datastructures import Code


def parse_criterions(el):
    """Parse trigger requirements from a ``lineSelect`` element
    and return a list of concrete :class:`Criterion` instances.
    """
    criterions = []
    for child in el.xpath('|'.join(VALID_CRITERIONS)):
        assert child.tag in CRITERION_MAP
        criterions.append(CRITERION_MAP[child.tag].fromxml(child))
    return criterions


class Criterion(object):

    @classmethod
    def fromxml(cls, element):
        return cls(element.text)

    def __init__(self, value):
        self.value = value
        self.params = self.parse_value(value)

    def is_satisfied(self, dto):
        raise NotImplementedError("Subclasses must override this method.")


class IsPopulated(Criterion):

    def parse_value(self, value):
        return set([x.strip() for x in value.split(',')])

    def is_satisfied(self, dto):
        # The isPopulated trigger condition can have multiple arguments
        # and is satisfied only if all arguments, including at least one
        # of a set of elements within an argument, meet the condition
        # of being populated (NEN 2011: 47).
        return any([dto.is_populated(x) for x in self.params])


class IsNotPopulated(Criterion):

    def parse_value(self, value):
        return set([x.strip() for x in value.split(',')])

    def is_satisfied(self, dto):
        # The isNotPopulated trigger condition ... is satisfied only if
        # all arguments, including at least one of a set of elements
        # within an argument, are not populated, that is, null or an
        # empty string (NEN 2011: 47).
        return not any([dto.is_populated(x) for x in self.params])


class HasValue(Criterion):

    def parse_value(self, value):
        code, literal = [x.strip() for x in value.split(';')]
        self.code = Code.fromstring(code)
        self.literal = literal.strip('"')

    def is_satisfied(self, dto):
        return dto.get(self.code) == self.literal


CRITERION_MAP = {
    'isPopulated': IsPopulated,
    'isNotPopulated': IsNotPopulated,
    'hasValue': HasValue
}


VALID_CRITERIONS = list(CRITERION_MAP.keys())


