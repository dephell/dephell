# app
from .app_dirs import get_cache_dir, get_data_dir
from .manager import Config


config = Config()


__all__ = ['Config', 'config', 'get_cache_dir', 'get_data_dir']
