import unittest

from i18n import resource_loader
from i18n.resource_loader import I18nFileLoadError

class TestFileLoader(unittest.TestCase):
    def setUp(self):
        resource_loader.loaders = {}

    def test_nonexisting_extension(self):
        with self.assertRaisesRegexp(I18nFileLoadError, "no loader .*"):
            resource_loader.load_resource("foo.bar", "baz")

    def test_wrong_loader_registration(self):
        class WrongLoader(object):
            pass
        with self.assertRaises(ValueError):
            resource_loader.register_loader(WrongLoader, [])

    def test_loader_registration(self):
        with self.assertRaisesRegexp(I18nFileLoadError, "no loader .*"):
            resource_loader.load_resource("foo.py", "bar")
        resource_loader.init_python_loader()
        with self.assertRaisesRegexp(I18nFileLoadError, "error loading file .*"):
            resource_loader.load_resource("foo.py", "bar")


suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
