import os.path

from . import config
from .loaders.loader import I18nFileLoadError
from . import translations

loaders = {}


def register_loader(loader_class, supported_extensions):
    if not hasattr(loader_class, "load_resource"):
        raise ValueError("loader class should have a 'load_resource' method")

    for extension in supported_extensions:
        loaders[extension] = loader_class()


def load_resource(filename, root_data):
    extension = os.path.splitext(filename)[1][1:]
    if extension not in loaders:
        raise I18nFileLoadError("no loader available for extension {0}".format(extension))
    return getattr(loaders[extension], "load_resource")(filename, root_data)


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


def get_namespace_from_filepath(filename):
    namespace = os.path.dirname(filename).strip(os.sep).replace(os.sep, config.get('namespace_delimiter'))
    if '{namespace}' in config.get('filename_format'):
        try:
            splitted_filename = os.path.basename(filename).split('.')
            if namespace:
                namespace += config.get('namespace_delimiter')
            namespace += splitted_filename[config.get('filename_format').index('{namespace}')]
        except ValueError:
            raise I18nFileLoadError("incorrect file format.")
    return namespace


def load_translation_file(filename, base_directory, locale=config.get('locale')):
    skip_locale_root_data = config.get('skip_locale_root_data')
    root_data = None if skip_locale_root_data else locale
    translations_dic = load_resource(os.path.join(base_directory, filename), root_data)
    namespace = get_namespace_from_filepath(filename)
    load_translation_dic(translations_dic, namespace, locale)


def load_translation_dic(dic, namespace, locale):
    if namespace:
        namespace += config.get('namespace_delimiter')
    for key, value in dic.items():
        if type(value) == dict and not ("one" in value and "many" in value):
            load_translation_dic(value, namespace + key, locale)
        else:
            translations.add(namespace + key, value, locale)


def load_directory(directory, locale=config.get('locale')):
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        if os.path.isfile(path) and path.endswith(config.get('file_format')):
            if '{locale}' in config.get('filename_format') and not locale in f:
                continue
            load_translation_file(f, directory, locale)


def search_translation(key, locale=config.get('locale')):
    splitted_key = key.split(config.get('namespace_delimiter'))
    if not splitted_key:
        return
    namespace = splitted_key[:-1]
    if not namespace and '{namespace}' not in config.get('filename_format'):
        for directory in config.get('load_path'):
            load_directory(directory, locale)
    else:
        for directory in config.get('load_path'):
            recursive_search_dir(namespace, '', directory, locale)


def recursive_search_dir(splitted_namespace, directory, root_dir, locale=config.get('locale')):
    if not splitted_namespace:
        return
    seeked_file = config.get('filename_format').format(namespace=splitted_namespace[0], format=config.get('file_format'), locale=locale)
    dir_content = os.listdir(os.path.join(root_dir, directory))
    if seeked_file in dir_content:
        load_translation_file(os.path.join(directory, seeked_file), root_dir, locale)
    elif splitted_namespace[0] in dir_content:
        recursive_search_dir(splitted_namespace[1:], os.path.join(directory, splitted_namespace[0]), root_dir, locale)
