import helper
import os

CONFIG = helper.parse_config("inscreen_config.txt")
INADDR_ANY = "0.0.0.0"
MAX_RESPONSE_PER_MINUTE = 20
PORT = int(os.environ.get("PORT", "8443"))
TIME_LIMIT = 3
TOKEN = CONFIG.token[0]
URL = "https://inscreen.herokuapp.com/"
