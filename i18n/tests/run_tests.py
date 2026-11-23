import unittest

from i18n.tests.loader_tests import TestFileLoader
from i18n.tests.locale_tests import TestTranslationLocale
from i18n.tests.preload_tests import TestPreload
from i18n.tests.package_tests import TestPackageResources
from i18n.tests.translation_tests import TestTranslationFormat


def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestFileLoader))
    suite.addTest(loader.loadTestsFromTestCase(TestTranslationLocale))
    suite.addTest(loader.loadTestsFromTestCase(TestPackageResources))
    suite.addTest(loader.loadTestsFromTestCase(TestTranslationFormat))
    suite.addTest(loader.loadTestsFromTestCase(TestPreload))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
