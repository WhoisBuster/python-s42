from os.path import join

from s42.const import TEMPLATE_DIR
from s42.const import TEMPLATE_FILENAME
from s42.template.base import Template


__all__ = [
    'Template',
    'get_template'
]


def get_template(country_code, s42_version='6', patdl_version='2.6'):
    """Return a :class:`~s42.template.base.Template` instance
    by providing an ISO 3166 Alpha 2 country code, the S42
    version and the PATDL version.
    """
    src = TEMPLATE_FILENAME.format(
        s42_version, patdl_version, country_code)
    return Template.fromfilepath(join(TEMPLATE_DIR, src))
