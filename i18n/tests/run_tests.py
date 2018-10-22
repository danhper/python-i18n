import unittest

from i18n.tests.translation_tests import TestTranslationFormat

from i18n.tests.loader_tests import TestFileLoader


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(TestFileLoader))
    suite.addTest(unittest.makeSuite(TestTranslationFormat))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
