import functools
import operator

from s42.datastructures import Code
from s42.datastructures import LineIdentifier
from s42.template.node import ComponentNode
from s42.template.node import ElementNode
from s42.template.node import LineNode
from s42.template.node import SeparatorNode
from s42.template.node import ValueNode

def parse_lines(element):
    """Parse a list of :class:`~s42.datastructures.LineIdentifier`
    instance from a ``lineSelect`` element.
    """
    return [LineIdentifier.fromxml(x) for x in element.xpath('lineName')]
 

def line_factory(el):
    """Create a new :class:`Line` instance from an XML element."""
    assert len(parse_lines(el)) == 1
    identifier = parse_lines(el)[0]

    return Line.fromxml(identifier, el)


class Line(object):
    """Represents a line definition on an address template."""

    @property
    def identifier(self):
        return self._identifier

    @classmethod
    def fromxml(cls, identifier, element):
        components = []
        for child in element.xpath('lineComponent'):
            components.append(LineComponent.fromxml(child))

        return cls(identifier, components)

    def __init__(self, identifier, components):
        self._identifier = identifier
        self._components = components

    def as_node(self, template, dto):
        """Return a :class:`~s42.template.node.Line` instance representing
        a line on an address rendition.
        """
        node = LineNode(template, dto)
        for component in self.get_components(dto):
            node.add(component.as_node(template, dto))

        return node

    def get_components(self, dto):
        """Return all :class:`LineComponent` instances that are
        valid i.e. have one or more values.
        """
        return [c for c in self._components if c.is_valid(dto)]

    def __repr__(self):
        return "<Line: ({0}, {1})>".format(
            *map(repr, self.identifier)
        )


class RenditionOperator(object):
    CONCAT = 'CONCAT'

    @classmethod
    def fromxml(cls, element):
        kwargs = {}
        for child in element:
            tag = child.tag
            value = child.text
            if tag == 'operatorId':
                kwargs['operator_type'] = value
            elif tag == 'fldJustify':
                kwargs['justify'] = value
            elif tag == 'fldText':
                kwargs['text'] = value.strip("'")
            else:
                raise NotImplementedError("Unrecognized tag: " + tag)

        return cls(**kwargs)

    def __init__(self, operator_type, text=None, justify=None):
        self._text = text
        self._operator_type = operator_type
        self._justify = justify

        assert self._operator_type in [self.CONCAT]

    def __str__(self):
        return self._text


class LineComponent(object):
    Empty = type('Empty', (ValueError,), {})
    Missing = type('Missing', (ValueError,), {})

    @property
    def required_elements(self):
        return [x.code for x in self._elements if x.is_required()]

    @classmethod
    def fromxml(cls, element):
        elements = []
        kwargs = {}
        for child in element:
            tag = child.tag
            value = child.text
            if tag == 'elementData':
                elements.append(ElementData.fromxml(child))
            elif tag == 'componentId':
                kwargs['component_id'] = value
            elif tag == 'requiredIfSelected':
                kwargs['required'] = value == 'Y'
            elif tag == 'priority':
                kwargs['priority'] = value
            elif tag == 'renditionOperator':
                elements[-1].set_succeeding_rendition_operator(
                    RenditionOperator.fromxml(child))
            else:
                raise NotImplementedError("Unrecognized tag: " + tag)
            
        kwargs['elements'] = elements
        return cls(**kwargs)

    def __init__(self, component_id, elements, priority, required=False):
        self._component_id = component_id
        self._elements = elements
        self._priority = priority
        self._required = required

    def as_node(self, template, dto):
        node = ComponentNode(template, dto)

        # TODO: Template value preprocessing.
        for element in self._elements:
            if not dto.is_populated(element.code):
                continue
            node.add(element.as_node(template, dto))
        return node

    def is_valid(self, dto):
        return all([dto.is_populated(x) for x in self.required_elements])


class ElementData(object):

    @property
    def code(self):
        return self._code

    @classmethod
    def fromxml(cls, element):
        kwargs = {
            'required': False    
        }
        for child in element:
            value = child.text
            tag = child.tag
            if tag == 'elementId':
                kwargs['code'] = Code.fromstring(value)
            elif tag == 'elementDef':
                kwargs['name'] = value
            elif tag == 'fldJustify':
                kwargs['justify'] = value
            elif tag == 'posStart':
                kwargs['position'] = value
            elif tag == 'requiredIfSelected':
                kwargs['required'] = value == 'Y'
            elif tag == 'migrationPrecedence':
                kwargs['migration_precedence'] = value
            elif tag == 'elementDesc':
                # Description of the element. Currently not used.
                pass
            else:
                raise NotImplementedError("Unrecognized tag: " + tag)
        return cls(**kwargs)

    def __init__(self, code, name, justify='L', required=False,
        position=None, migration_precedence=None):
        self._code = code
        self._name = name
        self._justify = justify
        self._required = required
        self._position = position
        self._migration_precedence = migration_precedence
        self._succeeding_operator = None

    def as_node(self, template, dto):
        node = ElementNode(template, dto)
        node.add(ValueNode(template, dto, self._code))
        node.add(SeparatorNode(template, dto, self.get_succeeding_separator()))
        return node

    def is_required(self):
        return self._required

    def set_succeeding_rendition_operator(self, operator):
        self._succeeding_operator = operator

    def get_preceding_separator(self):
        return ''

    def get_succeeding_separator(self):
        return ' ' if not self._succeeding_operator\
            else str(self._succeeding_operator)

    def add_to_line(self, parts, value):
        parts.extend([value, self.get_succeeding_separator()])
