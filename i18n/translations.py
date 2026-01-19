from . import config

container = {}


def _normalize_locale(locale):
    if isinstance(locale, (list, tuple)):
        return locale[0] if locale else config.get("locale")
    return locale


def add(key, value, locale=None):
    if locale is None:
        locale = config.get("locale")
    locale = _normalize_locale(locale)
    container.setdefault(locale, {})[key] = value


def has(key, locale=None):
    if locale is None:
        locale = config.get("locale")
    locale = _normalize_locale(locale)
    return key in container.get(locale, {})


def get(key, locale=None):
    if locale is None:
        locale = config.get("locale")
    locale = _normalize_locale(locale)
    return container[locale][key]
