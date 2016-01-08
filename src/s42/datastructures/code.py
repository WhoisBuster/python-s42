import re

from s42.const import CODE_PATTERN
from s42.const import HIERARCHY

CODE_RE = re.compile("^{0}$".format(CODE_PATTERN))


class Code(object):
    """Represents a S42 element identifier."""

    @property
    def base(self):
        return type(self).fromstring(self._base)

    @property
    def default(self):
        return self._default

    @classmethod
    def fromstring(cls, code):
        # An element sub-type code consists of the code of the element of
        # which it is a sub-type, followed by a hyphen and an identifier
        # consisting of a single digit identifying instances, followed
        # by a hyphen and ending with a single digit identifying parts.
        # The value of each single digit in the element sub-type code is
        # zero if the element sub-type is latent in that dimension,
        # and from one to nine if it is present. As a convention, when
        # using an element directly in a template, the format xx.yy and
        # the format xx.yy-z-z with each z taking the value of zero are 
        # considered equivalent (NEN 2011:31).
        try:
            kwargs = CODE_RE.match(code).groupdict()
        except AttributeError:
            raise ValueError("Invalid code: " + code)
        return cls(**kwargs)

    def __init__(self, code, subtype, instance=None, part=None, issuer=None):
        self._code = code
        self._subtype = subtype
        self._instance = instance or None
        self._part = part or None
        self._issuer = issuer or 'U'
        self._default = self
        self._base = "{0}{1}.{2}".format(issuer, code, subtype)
        if HIERARCHY.get(self._base) and not bool(instance):
            self._default = type(self).fromstring(HIERARCHY[self._base][0])

    def is_base(self):
        return self._instance is None

    def __hash__(self):
        return hash(tuple(self))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __iter__(self):
        return iter(str(self))

    def __str__(self):
        element = "{0}{1}.{2}".format(
            self._issuer, self._code, self._subtype)
        if self._instance is not None:
            assert self._part is not None
            element += "-{0}-{1}".format(self._instance, self._part)
        return element

    def __repr__(self):
        return "<Code: {0}>".format(str(self))
