import datetime
import helper
import logging
import time
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram.files.inputmedia import InputMediaPhoto

config_filename = "inscreen_config.txt"
config = helper.parseConfig(config_filename)

updater = Updater(token=config.token, use_context=True)
dispatcher = updater.dispatcher
