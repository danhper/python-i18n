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


config = {
    'file_name_format': '{filename}.{locale}.{format}',
    'file_format': 'yml' if yaml_available else 'json' if json_available else 'py',
    'available_locales': ['en'],
    'locale': 'en',
    'fallback': 'en',
}

def current_locale():
    return config['locale']

def load(filename):
    with open(filename, 'r') as f:
        pass
