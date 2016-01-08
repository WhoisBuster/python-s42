import collections

from s42.datastructures import LineIdentifier


def selector_factory(template, element):
    """Return the appropriate instance of a :class:`Trigger`
    subclass using an XML element.
    """
    assert element.tag in TAG_MAPPING
    return TAG_MAPPING[element.tag].fromxml(template, element)


class LineSelector(object):

    @property
    def lines(self):
        raise NotImplementedError("This property is retired.")

    @classmethod
    def fromxml(cls, element):
        raise NotImplementedError("Subclasses must override this method.")

    @staticmethod
    def parse_line_triggers(template, element):
        """Parse the trigger conditions and the ``lineName`` elements
        they yield from a ``triggerConditions`` element.
        """
        # Trigger conditions are followed by one or more line candidates, 
        # and if the conditions are satisfied, the immediately following
        # line candidates, which may explicitly include or implicitly
        # exclude line components, will be selected into the initial
        # rendition. Each line candidate and line component with all of
        # its elements and operators are defined in a lineData section.
        # Whenever one set of trigger conditions within a lineSelect block 
        # has been satisfied, none of the others are evaluated. If a line
        # candidate is selected but user preferences indicate that it is
        # to be suppressed, it is not brought forward (NEN 2011: 47).
        groups = []
        new_group = True
        i = -1
        preceding_tag = None
        for child in element:
            tag = child.tag
            value = child.text
            assert tag in ['lineName'] + VALID_TRIGGER_CONDITIONS, tag

            if (preceding_tag == 'lineName') and (tag in VALID_TRIGGER_CONDITIONS):
                new_group = True

            if new_group:
                groups.append({'triggers': [], 'lines': []})
                i += 1
                new_group = False

            key = 'lines' if tag == 'lineName' else 'triggers'
            groups[i][key].append(child)

            preceding_tag = tag

        return LineSelector._groups_from_elements(template, groups)

    @staticmethod
    def _groups_from_elements(template, groups):
        return [Trigger.fromelements(template, **x) for x in groups]

    @classmethod
    def fromxml(cls, template, element):
        return cls(template, cls.parse_line_triggers(template, element))

    def __init__(self, template, groups):
        self._groups = groups

    def get_lines(self, dto):
        """Get a list of :class:`~s42.template.line.Line` instance
        based on the elements provided by `dto`.
        """
        lines = []
        for trigger in self._groups:
            if not trigger.is_satisfied(dto):
                continue
            lines.extend(trigger.lines)

        return lines


class Trigger(object):
    """The abstract base class for all triggers."""

    @property
    def lines(self):
        return self._lines

    @classmethod
    def fromelements(cls, template, triggers, lines):
        args = collections.defaultdict(list)
        for element in triggers:
            args[element.tag].append(element)

        return Trigger(template,
            [TriggerCondition.factory(template, x, *y) for x, y in args.items()],
            [LineIdentifier.fromxml(x) for x in lines]
        )

    def __init__(self, template, conditions, lines):
        self._conditions = conditions
        self._lines = lines

    def is_satisfied(self, dto):
        return all([x.is_satisfied(dto) for x in self._conditions])


class TriggerCondition(object):

    @staticmethod
    def parse_arg(template, element):
        raise NotImplementedError("Subclasses must override this method.")

    @staticmethod
    def factory(template, tag, *args):
        """Return a :class:`TriggerCondition` implementation based
        on the XML tag of an element.
        """
        return TRIGGER_CONDITION_MAPPING[tag].fromelements(template, *args)

    @classmethod
    def fromelements(cls, template, *elements):
        """Create a new trigger condition from an XML element."""
        return cls(template, args=[cls.parse_arg(template, x) for x in elements])

    def __init__(self, template, args=None):
        self.args = args
        self.template = template

    def is_satisfied(self, dto):
        return all(map(lambda x: self.process_arg(dto, *x), self.args))


class DefaultCase(TriggerCondition):

    @classmethod
    def fromelements(cls, template, *elements):
        return cls(template)

    def is_satisfied(self, value):
        return True


class IsPopulated(TriggerCondition):

    @staticmethod
    def parse_arg(template, element):
        return [list(map(str.strip, x.split(template.separator))) for x in 
            map(str.strip, element.text.split(template.sequencer))]

    def process_arg(self, dto, *codes):
        # The isPopulated trigger condition can have multiple arguments
        # and is satisfied only if all arguments, including at least one
        # of a set of elements within an argument, meet the condition
        # of being populated (NEN 2011: 47).
        is_satisfied = False
        for codeset in codes:
            is_satisfied |= all(map(dto.is_populated, codeset))

        return is_satisfied


class IsNotPopulated(TriggerCondition):

    @staticmethod
    def parse_arg(template, element):
        return [list(map(str.strip, x.split(template.separator))) for x in 
            map(str.strip, element.text.split(template.sequencer))]

    def process_arg(self, dto, *codes):
        # The isNotPopulated trigger condition has the same options
        # and is satisfied only if all arguments, including at least
        # one of a set of elements within an argument, are not populated,
        # that is, null or an empty string.
        is_satisfied = False
        for codeset in codes:
            is_satisfied |= not any(map(dto.is_populated, codeset))

        return is_satisfied



class HasValue(TriggerCondition):

    @staticmethod
    def parse_arg(template, element):
        f = lambda x: x.strip().strip('"')
        return list(map(f, element.text.split(template.separator)))

    def process_arg(self, dto, code, value):
        # The hasValue trigger condition can test whether an element
        # has a particular value, or a value within a range of values,
        # or whether an element has the same value as another
        # element (NEN 2011: 47).
        return dto.get(code) == value


class HasResult(TriggerCondition):

    @staticmethod
    def parse_arg(template, element):
        return list(map(lambda x: str.strip(x).strip('"'),
            element.text.split(template.separator)))

    def process_arg(self, dto, func, retval):
        # The hasResult trigger condition and the preCondition trigger condition
        # compare the result of an external called function to a specified value.
        # These are the only trigger conditions that can accept elements as input
        # parameters. If present, the parameters are enclosed in parentheses after 
        # the function name and delimited by the default sequencer (NEN 2011: 47).
        return self.template.invoke_procedure(func, dto) == retval


TAG_MAPPING = {
    'lineSelect': LineSelector
}


TRIGGER_CONDITION_MAPPING = {
    'defaultCase': DefaultCase,
    'hasValue': HasValue,
    'isPopulated': IsPopulated,
    'isNotPopulated': IsNotPopulated,
    'hasResult': HasResult
}


VALID_TRIGGER_CONDITIONS = list(TRIGGER_CONDITION_MAPPING.keys())
