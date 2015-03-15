from . import config

container = {}


def add(key, value, locale=config.get('locale')):
    container.setdefault(locale, {})[key] = value


def has(key, locale=config.get('locale')):
    return key in container.get(locale, {})


def get(key, locale=config.get('locale')):
    return container[locale][key]
