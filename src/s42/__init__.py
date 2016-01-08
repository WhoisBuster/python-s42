from s42.const import ADDRESS_MAP
from s42.template import get_template
from s42.datastructures import Country

__all__ = ['render']


def render(country_code, fields):
    tpl = get_template(country_code)
    return tpl.render(fields)


def mnemonic_to_codes(country, dto, pop=True):
    elements = {}
    f = dict.get if not pop else dict.pop
    for name in list(dto.keys()):
        if name not in ADDRESS_MAP[country]:
            continue
        code = ADDRESS_MAP[country][name]
        elements[code] = f(dto, name)

    return elements


def create_dps(dto, pop=False):
    """Create a new delivery point specification from a
    Python dictionary.
    """
    # If the dictionary has a country member, it is assumed
    # to be a s42.datastructures.Country or an iso3166.ISO3166
    # instance.
    country = dto.pop('country')
    if country is None:
        raise TypeError(
            "The Data Transfer Object must declare a `country` member.")

    iso = Country.fromcode(country)
    dto['country_name'] = str(iso)
    return iso, mnemonic_to_codes(iso.numeric3, dto, pop=pop)

