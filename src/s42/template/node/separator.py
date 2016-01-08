from s42.template.node.base import Node


class SeparatorNode(Node):

    def __init__(self, template, dto, value):
        Node.__init__(self, template, dto)

        # value contains the character that is used to
        # join left value node with the right value node.
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return "<SeparatorNode: {0}>".format(self.value or 'DEFAULT')
