from os.path import abspath
from os.path import dirname
from os.path import join
import collections
import json
import re

SHARE_DIR = '/usr/share/s42'

TEMPLATE_DIR = join(SHARE_DIR, 'patdl')

FIXTURE_DIR = join(SHARE_DIR, 'fixtures')

TEMPLATE_FILENAME = "S42-{0}-{2}-PATDL.v.{1}.xml"


# Parse the S42 conceptual hierarchy by finding all element codes
# from the hierarchy XML file.
CODE_PATTERN = '(?:(?P<issuer>[A-Z]))?(?P<code>[0-9]{2})\.(?P<subtype>[0-9]{2})(?:\-(?P<instance>[0-9])\-(?P<part>[0-9]))?'
HIERARCHY = collections.defaultdict(list)

doc = open(join(SHARE_DIR, 'hierarchy.xml')).read()
for issuer, code, subtype, instance, part in re.findall(CODE_PATTERN, doc):
    base = "{0}{1}.{2}".format(issuer, code, subtype)
    if not instance:
        HIERARCHY[base] = []
        continue
    assert part
    HIERARCHY[base].append("{0}-{1}-{2}".format(base, instance, part))


#: A mapping of mnemmonic field names to S42 elements
ADDRESS_MAP = {
    '528' : { # The Netherlands
        'thoroughfare': "40.21-1-1",
        'street_number': "40.24",
        'postcode': "40.13",
        'town': "40.16",
        'country_name': "40.14",
        'door': "40.32",
        'building': '40.26-0-2'
    },
    '840': { # The United States
        'predirectional': "40.21-1-3",
        'postdirectional': "40.21-2-3",
        'thoroughfare': "40.21-1-1",
        'thoroughfare_type': "40.21-2-2",
        'street_number': "40.24",
        'postcode': "40.13-0-1",
        'postcode4': "40.13-0-2",
        'town': "40.16",
        'region': "40.15",
        'country_name': "40.14"
    }
}


ISO3166_MAP = {}
for element in json.load(open(abspath(join(dirname(__file__), 'iso3166.json')))):
    ISO3166_MAP[element.get('alpha2')] = element
    ISO3166_MAP[element.get('alpha3')] = element
    ISO3166_MAP[element.get('numeric3')] = element


del re
del join
del issuer
del code
del subtype
del instance
del part
del doc


