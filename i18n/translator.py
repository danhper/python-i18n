from string import Template

from . import config
from . import resource_loader
from . import translations

class TranslationFormatter(Template):
    delimiter = config.get('placeholder_delimiter')

    """docstring for TranslationFormatter"""
    def __init__(self, template):
        super(TranslationFormatter, self).__init__(template)

    def format(self, **kwargs):
        if config.get('error_on_missing_placeholder'):
            return self.substitute(**kwargs)
        else:
            return self.safe_substitute(**kwargs)

def t(key, **kwargs):
    locale = kwargs.pop('locale', config.get('locale'))
    if translations.has(key, locale):
        return t_(key, locale=locale, **kwargs)
    else:
        resource_loader.search_translation(key, locale)
        if translations.has(key, locale):
            return t_(key, locale=locale, **kwargs)
        elif locale != config.get('fallback'):
            return t(key, locale=config.get('fallback'), **kwargs)
    if config.get('error_on_missing_translation'):
        raise KeyError('key {0} not found'.format(key))
    else:
        return key

def t_(key, **kwargs):
    locale = kwargs.pop('locale', config.get('locale'))
    return TranslationFormatter(translations.get(key, locale=locale)).format(**kwargs)
