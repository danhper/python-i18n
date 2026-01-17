from . import config, resource_loader
from .resource_loader import I18nFileLoadError as I18nFileLoadError
from .resource_loader import load_config as load_config
from .resource_loader import register_loader as register_loader
from .translations import add as add_translation  # noqa: F401
from .translator import t as t

resource_loader.init_loaders()
load_path = config.get("load_path")
