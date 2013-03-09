import unittest

import i18n

class TestFileLoader(unittest.TestCase):
    def test_dummy(self):
        self.assertTrue(hasattr(i18n, 'resource_loader'))

suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
