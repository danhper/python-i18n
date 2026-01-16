from . import config, resource_loader
from .config import get as get, set as set
from .resource_loader import (
    I18nFileLoadError as I18nFileLoadError,
    load_config as load_config,
    register_loader as register_loader,
)
from .translations import add as add
from .translator import t as t


resource_loader.init_loaders()

load_path = config.get("load_path")
