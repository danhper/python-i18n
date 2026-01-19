# -*- encoding: utf-8 -*-
# type: ignore
from __future__ import unicode_literals

import os
import os.path
import pytest

from importlib import reload

from i18n import config, resource_loader, translations
from i18n.translator import t

RESOURCE_FOLDER = os.path.dirname(__file__) + os.sep + "resources" + os.sep


class TestTranslationFormat:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        resource_loader.init_loaders()
        reload(config)
        config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations")])
        translations.add("foo.hello", "Salut %{name} !", locale="fr")
        translations.add(
            "foo.basic_plural", {"one": "1 elem", "many": "%{count} elems"}
        )
        translations.add(
            "foo.plural",
            {
                "zero": "no mail",
                "one": "1 mail",
                "few": "only %{count} mails",
                "many": "%{count} mails",
            },
        )
        translations.add("foo.bad_plural", {"bar": "foo elems"})

    @pytest.fixture(autouse=True)
    def setup_method(self):
        config.set("error_on_missing_translation", False)
        config.set("error_on_missing_placeholder", False)
        config.set("fallback", "en")
        config.set("locale", "en")
        translations.add("foo.hi", "Hello %{name} !")

    def test_basic_translation(self):
        assert t("foo.normal_key") == "normal_value"

    def test_missing_translation(self):
        assert t("foo.inexistent") == "foo.inexistent"

    def test_missing_translation_error(self):
        config.set("error_on_missing_translation", True)
        with pytest.raises(KeyError):
            t("foo.inexistent")

    def test_locale_change(self):
        config.set("locale", "fr")
        assert t("foo.hello", name="Bob") == "Salut Bob !"

    def test_fallback(self):
        config.set("fallback", "fr")
        assert t("foo.hello", name="Bob") == "Salut Bob !"

    def test_fallback_from_resource(self):
        config.set("fallback", "ja")
        assert t("foo.fallback_key") == "フォールバック"

    def test_basic_placeholder(self):
        assert t("foo.hi", name="Bob") == "Hello Bob !"

    def test_missing_placeholder(self):
        assert t("foo.hi") == "Hello %{name} !"

    def test_missing_placeholder_error(self):
        config.set("error_on_missing_placeholder", True)
        with pytest.raises(KeyError):
            t("foo.hi")

    def test_basic_pluralization(self):
        assert t("foo.basic_plural", count=0) == "0 elems"
        assert t("foo.basic_plural", count=1) == "1 elem"
        assert t("foo.basic_plural", count=2) == "2 elems"

    def test_full_pluralization(self):
        assert t("foo.plural", count=0) == "no mail"
        assert t("foo.plural", count=1) == "1 mail"
        assert t("foo.plural", count=4) == "only 4 mails"
        assert t("foo.plural", count=12) == "12 mails"

    def test_bad_pluralization(self):
        config.set("error_on_missing_plural", False)
        assert t("foo.normal_key", count=5) == "normal_value"
        config.set("error_on_missing_plural", True)
        with pytest.raises(KeyError):
            t("foo.bad_plural", count=0)

    def test_default(self):
        assert t("inexistent_key", default="foo") == "foo"

    def test_skip_locale_root_data(self):
        config.set("filename_format", "{locale}.{format}")
        config.set("file_format", "json")
        config.set("locale", "gb")
        config.set("skip_locale_root_data", True)
        resource_loader.init_loaders()
        assert t("foo") == "Lorry"
        config.set("skip_locale_root_data", False)

    def test_skip_locale_root_data_nested_json_dict__default_locale(self):
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", "en")
        resource_loader.init_json_loader()
        assert t("COMMON.START") == "Start"

    def test_skip_locale_root_data_nested_json_dict__other_locale(self):
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", "en")
        resource_loader.init_json_loader()
        assert t("COMMON.EXECUTE", locale="pl") == "Wykonaj"
