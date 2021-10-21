"""
Verify the behavior of the ADM utility library
"""
from unittest import TestCase

import adm

class TestUtil(TestCase):

    def test_to_int(self):
        x = adm.to_int('1')
        self.assertEqual(x, 1)
        x = adm.to_int('100')
        self.assertEqual(x, 100)
        x = adm.to_int('-11')
        self.assertEqual(x, -11)
        x = adm.to_int(None)
        self.assertEqual(x, None)
        x = adm.to_int('none')
        self.assertEqual(x, None)
        x = adm.to_int('None')
        self.assertEqual(x, None)


if __name__ == '__main__':
    try:
        from test import test_support
    except ImportError:
        from test import support as test_support
    test_support.run_unittest(TestUtil)
