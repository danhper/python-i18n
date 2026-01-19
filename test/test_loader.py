#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# type: ignore
from __future__ import unicode_literals

import os
import os.path
import tempfile
import pytest

from importlib import reload

from i18n import config, resource_loader, translations
from i18n.config import json_available, yaml_available
from i18n.resource_loader import I18nFileLoadError
from i18n.translator import t

RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), "resources")


@pytest.fixture(autouse=True, scope="module")
def global_setup():
    resource_loader.loaders = {}
    translations.container = {}
    reload(config)
    config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations")])
    config.set("filename_format", "{namespace}.{locale}.{format}")
    config.set("encoding", "utf-8")


@pytest.fixture(autouse=True)
def reset_state():
    old_loaders = dict(resource_loader.loaders)
    old_container = dict(translations.container)
    old_config = dict(config.__dict__)
    yield
    resource_loader.loaders = old_loaders
    translations.container = old_container
    for k in list(config.__dict__.keys()):
        if k not in old_config:
            del config.__dict__[k]
    for k, v in old_config.items():
        config.__dict__[k] = v


def test_load_unavailable_extension():
    with pytest.raises(I18nFileLoadError) as excinfo:
        resource_loader.load_resource("foo.bar", "baz")
    assert "no loader" in str(excinfo.value)


def test_register_wrong_loader():
    class WrongLoader(object):
        pass

    with pytest.raises(ValueError):
        resource_loader.register_loader(WrongLoader, [])


def test_register_python_loader():
    resource_loader.init_python_loader()
    with pytest.raises(I18nFileLoadError) as excinfo:
        resource_loader.load_resource("foo.py", "bar")
    assert "error loading file" in str(excinfo.value)


@pytest.mark.skipif(not yaml_available, reason="yaml library not available")
def test_register_yaml_loader():
    resource_loader.init_yaml_loader()
    with pytest.raises(I18nFileLoadError) as excinfo:
        resource_loader.load_resource("foo.yml", "bar")
    assert "error loading file" in str(excinfo.value)


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_load_wrong_json_file():
    resource_loader.init_json_loader()
    with pytest.raises(I18nFileLoadError) as excinfo:
        resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"), "foo"
        )
    assert "error getting data" in str(excinfo.value)


@pytest.mark.skipif(not yaml_available, reason="yaml library not available")
def test_load_yaml_file():
    resource_loader.init_yaml_loader()
    data = resource_loader.load_resource(
        os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.yml"), "settings"
    )
    assert "foo" in data
    assert data["foo"] == "bar"


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_load_json_file():
    resource_loader.init_json_loader()
    data = resource_loader.load_resource(
        os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"), "settings"
    )
    assert "foo" in data
    assert data["foo"] == "bar"


def test_load_python_file():
    resource_loader.init_python_loader()
    data = resource_loader.load_resource(
        os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.py"), "settings"
    )
    assert "foo" in data
    assert data["foo"] == "bar"


@pytest.mark.skipif(not yaml_available, reason="yaml library not available")
def test_memoization_with_file():
    memoization_file_name = "memoize.en.yml"
    try:
        d = tempfile.TemporaryDirectory()
        tmp_dir_name = d.name
    except AttributeError:
        tmp_dir_name = tempfile.mkdtemp()
    with open("{}/{}".format(tmp_dir_name, memoization_file_name), "w") as fd:
        fd.write("en:\n  key: value")
    resource_loader.init_yaml_loader()
    resource_loader.load_translation_file(memoization_file_name, tmp_dir_name)
    assert t("memoize.key") == "value"
    import shutil

    shutil.rmtree(tmp_dir_name)
    assert t("memoize.key") == "value"


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_load_file_with_strange_encoding():
    resource_loader.init_json_loader()
    config.set("encoding", "euc-jp")
    data = resource_loader.load_resource(
        os.path.join(RESOURCE_FOLDER, "settings", "eucjp_config.json"), "settings"
    )
    assert "ほげ" in data
    assert data["ほげ"] == "ホゲ"


def test_get_namespace_from_filepath_with_filename():
    tests = {
        "foo": "foo.ja.yml",
        "foo.bar": os.path.join("foo", "bar.ja.yml"),
        "foo.bar.baz": os.path.join("foo", "bar", "baz.en.yml"),
    }
    for expected, test_val in tests.items():
        namespace = resource_loader.get_namespace_from_filepath(test_val)
        assert expected == namespace


def test_get_namespace_from_filepath_without_filename():
    tests = {
        "": "ja.yml",
        "foo": os.path.join("foo", "ja.yml"),
        "foo.bar": os.path.join("foo", "bar", "en.yml"),
    }
    config.set("filename_format", "{locale}.{format}")
    for expected, test_val in tests.items():
        namespace = resource_loader.get_namespace_from_filepath(test_val)
        assert expected == namespace


@pytest.mark.skipif(not yaml_available, reason="yaml library not available")
def test_load_translation_file():
    config.set("encoding", "utf-8")
    config.set("locale", "en")
    resource_loader.init_yaml_loader()
    resource_loader.load_translation_file(
        "foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations")
    )

    assert translations.has("normal_key")
    assert translations.has("parent.nested_key")


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_load_plural():
    config.set("encoding", "utf-8")
    config.set("locale", "en")
    resource_loader.init_yaml_loader()
    resource_loader.load_translation_file(
        "foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations")
    )
    assert translations.has("mail_number")
    translated_plural = translations.get("mail_number")
    assert isinstance(translated_plural, dict)
    assert translated_plural["zero"] == "You do not have any mail."
    assert translated_plural["one"] == "You have a new mail."
    assert translated_plural["many"] == "You have %{count} new mails."


@pytest.mark.skipif(not yaml_available, reason="yaml library not available")
def test_search_translation_yaml():
    config.set("encoding", "utf-8")
    config.set("locale", "en")
    resource_loader.init_yaml_loader()
    config.set("file_format", "yml")
    translations.container.clear()
    resource_loader.load_translation_file(
        "foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations")
    )
    assert translations.has("normal_key")


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_search_translation_json():
    config.set("encoding", "utf-8")
    config.set("locale", "en")
    resource_loader.init_json_loader()
    config.set("file_format", "json")

    resource_loader.search_translation("bar.baz.qux")
    assert translations.has("foo")


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_search_translation_without_ns():
    config.set("encoding", "utf-8")
    config.set("locale", "en")
    resource_loader.init_json_loader()
    config.set("file_format", "json")
    config.set("filename_format", "{locale}.{format}")
    resource_loader.search_translation("foo")
    assert translations.has("foo")


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_search_translation_without_ns_nested_dict__two_levels_neting__default_locale():
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


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_search_translation_without_ns_nested_dict__two_levels_neting__other_locale():
    config.set("encoding", "utf-8")
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


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_search_translation_without_ns_nested_dict__default_locale():
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


@pytest.mark.skipif(not json_available, reason="json library not available")
def test_search_translation_without_ns_nested_dict__other_locale():
    config.set("encoding", "utf-8")
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
