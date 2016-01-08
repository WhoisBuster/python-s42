from s42.template.node.base import Node


class ValueNode(Node):

    @property
    def value(self):
        return self.dto.get(self.code)

    def __init__(self, template, dto, code):
        Node.__init__(self, template, dto)
        self.code = code

    def is_element(self):
        """Return a boolean indicating if the :class:`Node` represents
        a S42 data element.
        """
        return True

    def __str__(self):
        return self.value

    def __repr__(self):
        return "<ValueNode: {0}>".format(self.value)
