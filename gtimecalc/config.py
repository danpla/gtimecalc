
import os

from gi.repository import GLib

from . import app_info


CONFIG_DIR = os.path.join(GLib.get_user_config_dir(), app_info.NAME)
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
