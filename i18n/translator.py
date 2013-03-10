from string import Template

from . import config

translations = {}

class TranslationFormatter(Template):
    delimiter = config.get("placeholder_delimiter")

    """docstring for TranslationFormatter"""
    def __init__(self, template):
        super(TranslationFormatter, self).__init__(template)

    def format(self, **kwargs):
        if config.get('error_on_missing'):
            return self.substitute(**kwargs)
        else:
            return self.safe_substitute(**kwargs)


def t(key, *args, **kwargs):
    pass
    # translated_string =
