import functools
import operator

from s42.template.node.base import Node


class LineNode(Node):

    @property
    def nodeseq(self):
        """Return all nodes in the tree as a single, sequential
        list of objects.
        """
        for component in self.children:
            for element in component:
                for atomic in element:
                    yield atomic

    def render(self):
        if not self.children:
            return ''

        output = ''
        nodes = list(self.nodeseq)
        for node in nodes:
            if (nodes[-1] == node) and not node.is_element():
                continue
            output += str(node)

        return output

