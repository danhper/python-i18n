try:
    __import__("yaml")
    yaml_available = True
except ImportError:
    yaml_available = False

try:
    __import__("json")
    json_available = True
except ImportError:
    json_available = False

settings = {
    'file_name_format': '{namespace}.{locale}.{format}',
    'file_format': 'yml' if yaml_available else 'json' if json_available else 'py',
    'available_locales': ['en'],
    'load_path': [],
    'locale': 'en',
    'fallback': 'en',
    'placeholder_delimiter': '%',
    'error_on_missing': False,
    'encoding': 'utf-8',
    'namespace_delimiter': '.',
    'dir_as_namespace': True
}

def set(key, value):
    settings[key] = value

def get(key):
    return settings[key]
