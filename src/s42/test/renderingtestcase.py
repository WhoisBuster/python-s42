from os.path import join
import unittest

from s42.datastructures import AddressDTO
from s42.test.utils import get_test_fixture
from s42.template import get_template


class RenderingTestCase(unittest.TestCase):
    country_code = None
    version = ('6', '2.6')

    @classmethod
    def factory(cls, country_code):
        """Create a new test case using an ISO 3166 country code."""
        return type(country_code + 'RenderingTestCase', (cls,), {
            'country_code': country_code
        })

    def setUp(self):
        self.template = get_template(self.country_code, *self.version)
        self.fixtures = get_test_fixture(self.country_code)

    def test_is_populated(self):
        for fixture in self.fixtures:
            dto = AddressDTO.fromdict(fixture['data'])
            for code in fixture.get('is_populated', []):
                self.assertTrue(dto.is_populated(code))

    def test_rendering(self):
        """Assert that the rendering of an S42 address datastructure
        produces the correct output.
        """
        for fixture in self.fixtures:
            if fixture.get('skip', False):
                continue
            dto = fixture['data']
            required = '\n'.join(tuple(fixture['lines']))
            actual = '\n'.join(tuple(self.template.render(dto)))
            self.assertEqual(required, actual)
