import os
from os.path import abspath

MUSICDL_ASSETS = "musicdl_assets"
ASSET_DIR = "assets"

SRC_CWD = os.path.dirname(__file__)
CONFIG_PATH = abspath(os.path.join(SRC_CWD, "..", "config.json"))
JSONDUMP_PATH = abspath(os.path.join(SRC_CWD, "..", ASSET_DIR, "jsondump.json"))
INSTRUCTINOS_PATH = abspath(os.path.join(SRC_CWD, "..", ASSET_DIR, "instructions.png"))
THUMBNAIL_FULLPATH = abspath(os.path.join(SRC_CWD, "..", MUSICDL_ASSETS, "thumb[1421209540].jpg")) 