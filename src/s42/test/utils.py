from os.path import join
import json

from s42.const import FIXTURE_DIR


def get_test_fixture(country_code):
    src = join(FIXTURE_DIR, country_code + '.json')
    return json.load(open(src))
