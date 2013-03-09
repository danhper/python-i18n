import unittest

from i18n import resource_loader

class TestFileLoader(unittest.TestCase):
    def test_nonexisting_extension(self):
        self.assertRaises(resource_loader.I18nFileLoadError, resource_loader.load_resource, "foo.bar")


suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
