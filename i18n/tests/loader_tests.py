import unittest

from i18n import resource_loader

class TestFileLoader(unittest.TestCase):
    def test_nonexisting_extension(self):
        self.assertRaisesRegexp(resource_loader.I18nFileLoadError, "no loader available for extension .*", resource_loader.load_resource, "foo.bar")

    def test_python_loader_registration(self):
        pass


suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
