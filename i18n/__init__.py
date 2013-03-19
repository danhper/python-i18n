from . import resource_loader
from .resource_loader import I18nFileLoadError, register_loader
from .translator import t
from .translations import add as add_translation
from . import config

resource_loader.init_loaders()

load_path = config.get('load_path')
