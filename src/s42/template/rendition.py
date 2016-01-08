import os

from s42.template.node import AddressNode


class AddressRendition(object):

    @property
    def lines(self):
        if self._lines is None:
            self._render()
        return self._lines

    def __init__(self, template, dto, abstract=False, sep=None):
        """Initialize a new :class:`AddressRendition` instance.

        Args:
            template: the :class:`~s42.template.Template` instance
                that is used to render the address.
            dto: a :class:`~s42.datastructures.AddressDTO` instance
                holding the address elements.
            abstract: a boolean indicating if the rendtion is abstract
                e.g. only the element descriptions are rendered instead
                of their actual values.
        """
        self._template = template
        self._dto = dto
        self._abstract = abstract
        self._lines = None
        self._candidates = []
        self._sep = os.linesep

    def is_abstract(self):
        """Return a boolean indicating if the :class:`AddressRendition`
        is abstract.
        """
        return self._abstract

    def _render(self):
        self._candidates = self._template.get_selected_lines(self._dto)
        node = AddressNode(self._template, self._dto)
        for line in self._candidates:
            node.add(line.as_node(self._template, self._dto))

        self._lines = node

    def __str__(self):
        return os.linesep.join(self.lines)

    def __iter__(self):
        return iter(self.lines)
