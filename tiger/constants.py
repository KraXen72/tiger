import os
from os.path import abspath

MUSICDL_ASSETS = "musicdl_assets"
ASSET_DIR = "assets"

SRC_CWD = os.path.join(os.getcwd(), "src")
CONFIG_PATH = abspath(os.path.join(SRC_CWD, "..", "config.json"))
JSONDUMP_PATH = abspath(os.path.join(SRC_CWD, "..", MUSICDL_ASSETS, "jsondump.json"))
INSTRUCTINOS_PATH = abspath(os.path.join(SRC_CWD, "..", ASSET_DIR, "instructions.png"))
THUMBNAIL_FULLPATH = abspath(os.path.join(SRC_CWD, "..", MUSICDL_ASSETS, "thumb[6UdQjCIPhDk].jpg")) 

# might remove this file, idk. 
# if you run some file that imports this as src.constants, and it's not musicdl.py, it crashes
# if you run musicdl.py and import as constants in other files, it crashes
# or, i might make this a proper submodule, with it's own directory.