from string import Template

from . import config

translations = {}

class TranslationFormatter(Template):
    delimiter = config.get('placeholder_delimiter')

    """docstring for TranslationFormatter"""
    def __init__(self, template):
        super(TranslationFormatter, self).__init__(template)

    def format(self, **kwargs):
        if config.get('error_on_missing'):
            return self.substitute(**kwargs)
        else:
            return self.safe_substitute(**kwargs)

def add_translation(key, value, locale=config.get('locale')):
    translations.setdefault(locale, {})[key] = value

def has(key, locale=config.get('locale')):
    return key in translations.get(locale, {})

def t(key, **kwargs):
    pass
    # translated_string =
