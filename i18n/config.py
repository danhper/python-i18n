
config = {
    'file_name_format': '{filename}.{locale}.{format}',
    'file_format': 'yml',
    'available_locales': ['en'],
    'locale': 'en',
    'fallback': 'en',
}

def current_locale():
    return config['locale']

def load(filename):
    with open(filename, 'r') as f:
        pass
