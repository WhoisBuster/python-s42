import collections

import lxml.etree as xml

from s42.datastructures import Code
from s42.datastructures import AddressDTO
from s42.template.rendition import AddressRendition
from s42.template.trigger import selector_factory
from s42.template.exc import TemplateDoesNotExist
from s42.template.lines import line_factory


class Template(object):
    """Represents a S42 PATDL template."""
    __preprocessors = collections.defaultdict(
        lambda: collections.defaultdict(list))
    __procedures = collections.defaultdict(dict)

    @property
    def selectors(self):
        return tuple(self.__selectors)

    @classmethod
    def fromfilepath(cls, src):
        """Instantiate a new :class:`Template` instance using a
        filepath.

        Args:
            str: a string holding the filepath to an XML file holding a
                PATDL template.

        Returns:
            :class:`Template`
        """
        try:
            with open(src, 'rb') as f:
                doc = f.read()
        except IOError:
            raise TemplateDoesNotExist([src])
        return cls(doc)

    def __init__(self, doc):
        """Instantiate a new :class:`Template` instance.

        Args:
            doc: a string holding the XML template definition.
        """
        self.__selectors = []
        self.__lines = collections.OrderedDict()

        root = xml.fromstring(doc)
        self.delimiter = root.xpath('//defaultDelimiter')[0].text.strip("'")
        self.separator = root.xpath('//defaultSeparator')[0].text.strip("'")
        self.sequencer = root.xpath('//defaultSequencer')[0].text.strip("'")
        self.collector = root.xpath('//defaultCollector')[0].text.strip("'")

        self._parse_selectors(root)
        self._parse_lines(root)

        for child in root.xpath('contentDefinition/templateIdentifier/*'):
            tag = child.tag
            value = child.text
            if tag == 'countryCode':
                self.country = value

    def get_selected_lines(self, dto):
        """Return a list of :class:`~s42.template.LineIdentifier` instances
        representing the lines of the address rendition that will be selected.
        
        Args:
            dto: a :class:`~s42.datastructures.AddressDTO` instance.

        Returns:
            list
        """
        lines = []
        for selector in self.selectors:
            candidates = selector.get_lines(dto)
            if not candidates:
                continue
            lines.extend([self._get_line(x) for x in candidates])
        return lines

    def render(self, dto, abstract=False):
        """Render an :class:`~s42.datastructures.AddressDTO` into a
        :class:`~s42.template.RenderedAddress` instance.
        """
        if isinstance(dto, dict):
            dto = AddressDTO.fromdict(dto)
        return AddressRendition(self, dto, abstract=abstract)

    def _parse_selectors(self, root):
        for el in root.xpath('//triggerConditions/lineSelect'):
            self.__selectors.append(selector_factory(self, el))

    def _parse_lines(self, root):
        for el in root.xpath('//lineData'):
            line = line_factory(el)
            self.__lines[line.identifier] = line

    def _get_line(self, identifier):
        return self.__lines[identifier]

    def preprocess_value(self, code, value):
        for p in self._get_preprocessors(code):
            value = p(self, value)
        return value

    def _get_preprocessors(self, code):
        return self.__preprocessors.get(self.country, {}).get(code, [])

    @classmethod
    def register_preprocessor(cls, country, code):
        code = Code.fromstring(code)
        def decorator(func):
            cls.__preprocessors[country][code].append(func)
        return decorator

    @classmethod
    def register_procedure(cls, country, func_name):
        def decorator(func):
            cls.__procedures[country][func_name] = func
        return decorator

    def invoke_procedure(self, func_name, dto):
        return self.__procedures[self.country][func_name](dto)


#: TODO: Build a real framework.
import re


@Template.register_preprocessor('NL','U40.13')
def nl_format_postcode(tpl, value):
    if re.match('[0-9]{4}[A-Z]{2}', value):
        value = value[:4] + ' ' + value[4:]
    return value.upper()


@Template.register_preprocessor('NL','U40.16')
def nl_town_uppercase(tpl, value):
    return ' ' + value.strip().upper()


@Template.register_preprocessor('NL','U40.17')
def nl_sector_uppercase(tpl, value):
    return value.strip().upper()


@Template.register_preprocessor('NL','U40.14')
def nl_country_uppercase(tpl, value):
    return value.strip().upper()


@Template.register_preprocessor('NL','U40.28')
def nl_format_extension_designation(tpl, value):
    return ('-' + value) if value[0].isdigit()\
        else (' ' + value)


@Template.register_procedure('US','US-RuralRouteTypeTest')
def us_rural_route_type_test(dto):
    # “US-RuralRouteTypeTest” rendition instruction

    # For each address:

    # If “street no or plot” populated then it is not a
    #     rural route address (result = N)

    # If “thoroughfare type” is populated then it is not a
    #     rural route address (result = N).

    # If “thoroughfare name” starts with ‘HC’ or ‘RR’
    #     If there is another non-blank character in the 
    #     “thoroughfare name”

    #         If the next non-blank character is from 0 through 9
    #         
    #         It is a rural route address (result = Y).

    # Otherwise it is not a rural route address (result = N).
    if dto.is_populated('U40.24'):
        result = False
    elif  dto.is_populated('U40.21-2-2'):
        result = False
    elif dto.is_populated('U40.21-1-1'):
        thoroughfare_name = dto.get('U40.21-1-1')
        result = re.match('^(RR|HC)\s[0-9].*') is not None
    else:
        result = False

    assert result is not None
    return 'Y' if result else 'N'

