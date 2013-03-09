import unittest

import sys
sys.path.append("../")
from i18n import resource_loader

class TestFileLoader(unittest.TestCase):
    def test_dummy(self):
        self.assertTrue(False)


suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
