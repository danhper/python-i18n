import os.path
import re
from importlib.resources import files

from . import config, translations
from .loaders.loader import I18nFileLoadError

loaders = {}

PLURALS = ["zero", "one", "few", "many", "other"]


def register_loader(loader_class, supported_extensions):
    if not hasattr(loader_class, "load_resource"):
        raise ValueError("loader class should have a 'load_resource' method")

    for extension in supported_extensions:
        loaders[extension] = loader_class()


def load_resource(filename, root_data):
    resource_name = filename.name if hasattr(filename, "read_text") else filename
    extension = os.path.splitext(resource_name)[1][1:]
    if extension not in loaders:
        raise I18nFileLoadError(f"no loader available for extension {extension}")
    return loaders[extension].load_resource(filename, root_data)


def init_loaders():
    init_python_loader()
    if config.yaml_available:
        init_yaml_loader()
    if config.json_available:
        init_json_loader()


def init_python_loader():
    from .loaders.python_loader import PythonLoader

    register_loader(PythonLoader, ["py"])


def init_yaml_loader():
    from .loaders.yaml_loader import YamlLoader

    register_loader(YamlLoader, ["yml", "yaml"])


def init_json_loader():
    from .loaders.json_loader import JsonLoader

    register_loader(JsonLoader, ["json"])


def load_config(filename):
    settings_data = load_resource(filename, "settings")
    for key, value in settings_data.items():
        config.settings[key] = value


def get_namespace_from_filepath(filename, locale=None):
    namespace = (
        os.path.dirname(filename)
        .strip(os.sep)
        .replace(os.sep, config.get("namespace_delimiter"))
    )
    if "{namespace}" in config.get("filename_format"):
        pattern = (
            re.escape(config.get("filename_format"))
            .replace(r"\{namespace\}", "(?P<namespace>.+)")
            .replace(r"\{locale\}", re.escape(locale) if locale is not None else ".+?")
            .replace(r"\{format\}", "[^.]+")
        )
        match = re.fullmatch(pattern, os.path.basename(filename))
        if match is None:
            raise I18nFileLoadError("incorrect file format.")
        if namespace:
            namespace += config.get("namespace_delimiter")
        namespace += match.group("namespace")
    return namespace


def load_translation_file(filename, base_directory, locale=None):
    if locale is None:
        locale = config.get("locale")
    skip_locale_root_data = config.get("skip_locale_root_data")
    root_data = None if skip_locale_root_data else locale
    translations_dic = load_resource(os.path.join(base_directory, filename), root_data)
    namespace = get_namespace_from_filepath(filename, locale)
    load_translation_dic(translations_dic, namespace, locale)


def load_translation_dic(dic, namespace, locale):
    if namespace:
        namespace += config.get("namespace_delimiter")
    for key, value in dic.items():
        if isinstance(value, dict) and len(set(PLURALS).intersection(value)) < 2:
            load_translation_dic(value, namespace + key, locale)
        else:
            translations.add(namespace + key, value, locale)


def load_directory(directory, locale=None):
    if locale is None:
        locale = config.get("locale")
    filename_format = config.get("filename_format")
    filename_pattern = (
        re.escape(filename_format)
        .replace(r"\{locale\}", re.escape(locale))
        .replace(r"\{format\}", re.escape(config.get("file_format")))
        .replace(r"\{namespace\}", ".+")
    )
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        if os.path.isfile(path) and path.endswith(config.get("file_format")):
            if re.fullmatch(filename_pattern, f) is None:
                continue
            load_translation_file(f, directory, locale)


def load_all(locales=None):
    """Eagerly load configured translation files, including directory namespaces."""
    if locales is None:
        locales = config.get("available_locales")
    patterns = [
        (
            locale,
            re.compile(
                re.escape(config.get("filename_format"))
                .replace(r"\{locale\}", re.escape(locale))
                .replace(r"\{format\}", re.escape(config.get("file_format")))
                .replace(r"\{namespace\}", ".+")
            ),
        )
        for locale in locales
    ]

    def raise_walk_error(error):
        raise error

    for root in config.get("load_path"):
        for directory, subdirectories, filenames in os.walk(
            root, onerror=raise_walk_error
        ):
            subdirectories.sort()
            for filename in sorted(filenames):
                for locale, pattern in patterns:
                    if pattern.fullmatch(filename):
                        relative_path = os.path.relpath(
                            os.path.join(directory, filename), root
                        )
                        load_translation_file(relative_path, root, locale)


def search_translation(key, locale=None):
    if locale is None:
        locale = config.get("locale")
    splitted_key = key.split(config.get("namespace_delimiter"))
    if not splitted_key:
        return
    namespace = splitted_key[:-1]
    if not namespace and "{namespace}" not in config.get("filename_format"):
        for directory in config.get("load_path"):
            load_directory(directory, locale)
    else:
        for directory in config.get("load_path"):
            recursive_search_dir(namespace, "", directory, locale)
    for package in config.get("load_package_path"):
        search_package(package, namespace, locale)


def search_package(package, namespace, locale):
    if config.get("file_format") == "py":
        raise I18nFileLoadError("package resources require a text-based loader")
    root = files(package)
    filename_format = config.get("filename_format")
    has_filename_namespace = "{namespace}" in filename_format
    if not namespace and has_filename_namespace:
        return
    directories = []
    parts = namespace if has_filename_namespace else [*namespace, ""]
    for part in parts:
        filename = filename_format.format(
            namespace=part, format=config.get("file_format"), locale=locale
        )
        resource = root.joinpath(filename)
        # Early 3.9 zipfile.Path.is_file() reports missing entries as files,
        # and Traversable has no exists(), so confirm the name is listed.
        names = {entry.name for entry in root.iterdir()}
        if filename in names and resource.is_file():
            root_data = None if config.get("skip_locale_root_data") else locale
            data = load_resource(resource, root_data)
            relative_name = os.path.join(*(directories + [filename]))
            load_translation_dic(
                data, get_namespace_from_filepath(relative_name, locale), locale
            )
            if has_filename_namespace:
                return
        if not part:
            return
        subdirectory = root.joinpath(part)
        if not subdirectory.is_dir():
            return
        directories.append(part)
        root = subdirectory


def recursive_search_dir(splitted_namespace, directory, root_dir, locale=None):
    if locale is None:
        locale = config.get("locale")
    filename_format = config.get("filename_format")
    has_filename_namespace = "{namespace}" in filename_format
    if not splitted_namespace and has_filename_namespace:
        return
    seeked_file = filename_format.format(
        namespace=splitted_namespace[0] if splitted_namespace else "",
        format=config.get("file_format"),
        locale=locale,
    )
    search_directory = os.path.join(root_dir, directory)
    dir_content = os.listdir(search_directory)
    if seeked_file in dir_content and os.path.isfile(
        os.path.join(search_directory, seeked_file)
    ):
        load_translation_file(os.path.join(directory, seeked_file), root_dir, locale)
        if has_filename_namespace:
            return
    if splitted_namespace and splitted_namespace[0] in dir_content and os.path.isdir(
        os.path.join(search_directory, splitted_namespace[0])
    ):
        recursive_search_dir(
            splitted_namespace[1:],
            os.path.join(directory, splitted_namespace[0]),
            root_dir,
            locale,
        )
