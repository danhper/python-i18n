from . import config, resource_loader
from .config import get as get
from .config import set as set
from .resource_loader import I18nFileLoadError as I18nFileLoadError
from .resource_loader import load_all as load_all
from .resource_loader import load_config as load_config
from .resource_loader import register_loader as register_loader
from .translations import add as add_translation
from .translator import t as t

__all__ = [
    "I18nFileLoadError",
    "add_translation",
    "config",
    "get",
    "load_all",
    "load_config",
    "load_package_path",
    "load_path",
    "register_loader",
    "resource_loader",
    "set",
    "t",
]

resource_loader.init_loaders()

# Values are resolved from the current configuration by __getattr__.
load_path: list
load_package_path: list


def __getattr__(name):
    if name in ("load_path", "load_package_path"):
        return config.get(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(globals().keys() | {"load_path", "load_package_path"})
