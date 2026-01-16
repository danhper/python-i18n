import unittest

from i18n.tests.loader_tests import TestFileLoader
from i18n.tests.translation_tests import TestTranslationFormat


def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestFileLoader))
    suite.addTest(loader.loadTestsFromTestCase(TestTranslationFormat))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
