try:
    from iso3166.country import ISO3166 as Country
except ImportError:
    from s42.const import ISO3166_MAP


    class Country(object):
        """Represents an ISO 3166 data element."""

        @property
        def alpha2(self):
            return self._alpha2

        @property
        def numeric3(self):
            return self._numeric3

        @classmethod
        def fromcode(cls, code):
            return cls(**ISO3166_MAP[code])\
                if not isinstance(code, cls)\
                else code

        def __init__(self, name, alpha2, alpha3, numeric3, fips):
            self._name = name
            self._alpha2 = alpha2
            self._alpha3 = alpha3
            self._numeric3 = numeric3
            self._fips = fips

        def __int__(self):
            return int(self._numeric3)

        def __str__(self):
            return self._name

        def __repr__(self):
            return "Country(name={0}, alpha2={1}, alpha3={2}, numeric3={3})".format(
                repr(self._name),
                repr(self._alpha2),
                repr(self._alpha3),
                repr(self._numeric3)
            )
