# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import os
import os.path
import tempfile
import unittest
import pytest

from importlib import reload

from i18n import config, resource_loader, translations
from i18n.config import json_available, yaml_available
from i18n.resource_loader import I18nFileLoadError
from i18n.translator import t

RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), "resources")


class TestFileLoader:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        resource_loader.loaders = {}
        translations.container = {}
        reload(config)
        config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations")])
        config.set("filename_format", "{namespace}.{locale}.{format}")
        config.set("encoding", "utf-8")

    def test_load_unavailable_extension(self):
        with pytest.raises(I18nFileLoadError) as excinfo:
            resource_loader.load_resource("foo.bar", "baz")
        assert "no loader" in str(excinfo.value)

    def test_register_wrong_loader(self):
        class WrongLoader(object):
            pass

        with pytest.raises(ValueError):
            resource_loader.register_loader(WrongLoader, [])

    def test_register_python_loader(self):
        resource_loader.init_python_loader()
        with pytest.raises(I18nFileLoadError) as excinfo:
            resource_loader.load_resource("foo.py", "bar")
        assert "error loading file" in str(excinfo.value)

    @pytest.mark.skipif(not yaml_available, reason="yaml library not available")
    def test_register_yaml_loader(self):
        resource_loader.init_yaml_loader()
        with pytest.raises(I18nFileLoadError) as excinfo:
            resource_loader.load_resource("foo.yml", "bar")
        assert "error loading file" in str(excinfo.value)

    @pytest.mark.skipif(not json_available, reason="json library not available")
    def test_load_wrong_json_file(self):
        resource_loader.init_json_loader()
        with pytest.raises(I18nFileLoadError) as excinfo:
            resource_loader.load_resource(
                os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"), "foo"
            )
        assert "error getting data" in str(excinfo.value)

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_load_yaml_file(self):
        resource_loader.init_yaml_loader()
        data = resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.yml"), "settings"
        )
        assert "foo" in data
        assert data["foo"] == "bar"

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_json_file(self):
        resource_loader.init_json_loader()
        data = resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"), "settings"
        )
        assert "foo" in data
        assert data["foo"] == "bar"

    def test_load_python_file(self):
        resource_loader.init_python_loader()
        data = resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.py"), "settings"
        )
        assert "foo" in data
        assert data["foo"] == "bar"

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_memoization_with_file(self):
        """This test creates a temporary file with the help of the
        tempfile library and writes a simple key: value dictionary in it.
        It will then use that file to load the translations and, after having
        enabled memoization, try to access it, causing the file to be (hopefully)
        memoized. It will then _remove_ the temporary file and try to access again,
        asserting that an error is not raised, thus making sure the data is
        actually loaded from memory and not from disk access."""
        memoization_file_name = "memoize.en.yml"
        # create the file and write the data in it
        try:
            d = tempfile.TemporaryDirectory()
            tmp_dir_name = d.name
        except AttributeError:
            # we are running python2, use mkdtemp
            tmp_dir_name = tempfile.mkdtemp()
        fd = open("{}/{}".format(tmp_dir_name, memoization_file_name), "w")
        fd.write("en:\n  key: value")
        fd.close()
        # create the loader and pass the file to it
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file(memoization_file_name, tmp_dir_name)
        assert t("memoize.key") == "value"
        import shutil

        shutil.rmtree(tmp_dir_name)
        assert t("memoize.key") == "value"

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_file_with_strange_encoding(self):
        resource_loader.init_json_loader()
        config.set("encoding", "euc-jp")
        data = resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "eucjp_config.json"), "settings"
        )
        assert "ほげ" in data
        assert data["ほげ"] == "ホゲ"

    def test_get_namespace_from_filepath_with_filename(self):
        tests = {
            "foo": "foo.ja.yml",
            "foo.bar": os.path.join("foo", "bar.ja.yml"),
            "foo.bar.baz": os.path.join("foo", "bar", "baz.en.yml"),
        }
        for expected, test_val in tests.items():
            namespace = resource_loader.get_namespace_from_filepath(test_val)
            assert expected == namespace

    def test_get_namespace_from_filepath_without_filename(self):
        tests = {
            "": "ja.yml",
            "foo": os.path.join("foo", "ja.yml"),
            "foo.bar": os.path.join("foo", "bar", "en.yml"),
        }
        config.set("filename_format", "{locale}.{format}")
        for expected, test_val in tests.items():
            namespace = resource_loader.get_namespace_from_filepath(test_val)
            assert expected == namespace

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_load_translation_file(self):
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file(
            "foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations")
        )

        assert translations.has("foo.normal_key")
        assert translations.has("foo.parent.nested_key")

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_plural(self):
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file(
            "foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations")
        )
        assert translations.has("foo.mail_number")
        translated_plural = translations.get("foo.mail_number")
        assert isinstance(translated_plural, dict)
        assert translated_plural["zero"] == "You do not have any mail."
        assert translated_plural["one"] == "You have a new mail."
        assert translated_plural["many"] == "You have %{count} new mails."

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_search_translation_yaml(self):
        resource_loader.init_yaml_loader()
        config.set("file_format", "yml")
        resource_loader.search_translation("foo.normal_key")
        assert translations.has("foo.normal_key")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_json(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")

        resource_loader.search_translation("bar.baz.qux")
        assert translations.has("bar.baz.qux")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("filename_format", "{locale}.{format}")
        resource_loader.search_translation("foo")
        assert translations.has("foo")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__two_levels_neting__default_locale(
        self,
    ):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", ["en", "pl"])
        resource_loader.search_translation("COMMON.VERSION")
        assert translations.has("COMMON.VERSION")
        assert translations.get("COMMON.VERSION") == "version"

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__two_levels_neting__other_locale(
        self,
    ):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", ["en", "pl"])
        resource_loader.search_translation("COMMON.VERSION", locale="pl")
        assert translations.has("COMMON.VERSION", locale="pl")
        assert translations.get("COMMON.VERSION", locale="pl") == "wersja"

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__default_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", "en")
        resource_loader.search_translation("TOP_MENU.TOP_BAR.LOGS")
        assert translations.has("TOP_MENU.TOP_BAR.LOGS")
        assert translations.get("TOP_MENU.TOP_BAR.LOGS") == "Logs"

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__other_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", "en")
        resource_loader.search_translation("TOP_MENU.TOP_BAR.LOGS", locale="pl")
        assert translations.has("TOP_MENU.TOP_BAR.LOGS", locale="pl")
        assert translations.get("TOP_MENU.TOP_BAR.LOGS", locale="pl") == "Logi"
