from s42.template.node.base import Node
from s42.template.node.line import LineNode


class AddressNode(Node):

    def __iter__(self):
        return iter(self.children)
