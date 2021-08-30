import helper
import os

CONFIG = helper.parse_config("inscreen_config.txt")
INADDR_ANY = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8443"))
TIME_LIMIT = 3
TOKEN = CONFIG.token[0]
URL = "https://morning-harbor-80510.herokuapp.com/"
