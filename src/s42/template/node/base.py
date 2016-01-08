import collections
import functools
import operator


class Node(object):

    @property
    def children(self):
        return self._children

    def __init__(self, template, dto):
        self.template = template
        self.dto = dto
        self.parent = None
        self.siblings = []
        self._children = []

    def is_element(self):
        """Return a boolean indicating if the :class:`Node` represents
        a S42 data element.
        """
        return False

    def is_leaf(self):
        """Return a boolean indicating if the :class:`Node` represents
        a leaf node in the tree.
        """
        return bool(self.children)

    def is_rightmost(self):
        """Return a boolean indicating if the :class:`Node` is the rightmost
        sibling.
        """
        return self.siblings and (self.siblings[-1] == self)

    def render(self):
        if not self.children:
            return ''

        return functools.reduce(operator.add, self.children)\
            if (len(self.children) >= 1)\
            else self.children[0].render()

    def __str__(self):
        return self.render()

    def add(self, node):
        node.parent = self
        node.siblings = self._children
        self._children.append(node)

    def __iter__(self):
        return iter(self.children)
