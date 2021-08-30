import callback
import constants
import helper
import logging
import sys
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

helper.load()

updater = Updater(token=constants.TOKEN, use_context=True)
dispatcher = updater.dispatcher

# updater.bot.setWebhook(constants.URL + constants.TOKEN[0])


def stop(update, context):
    current_id = str(update.effective_chat.id)
    target_user_id = constants.CONFIG.target_id[0]

    if current_id == target_user_id:
        print("Saving data...")
        helper.save()
        print("Bye!")

        updater.stop()
        sys.exit()


config_filename = "inscreen_config.txt"
config = helper.parse_config(config_filename)
cb = callback.Callback(config)

nofollow_handler = CommandHandler("nofollow", cb.nofollow)
dispatcher.add_handler(nofollow_handler)

info_handler = CommandHandler("info", cb.info)
dispatcher.add_handler(info_handler)

clear_handler = CommandHandler("clear", cb.clear)
dispatcher.add_handler(clear_handler)

help_handler = CommandHandler("help", cb.help)
dispatcher.add_handler(help_handler)

received_photo_handler = MessageHandler(Filters.photo, cb.received_photo)
dispatcher.add_handler(received_photo_handler)

stop_handler = CommandHandler("stop", stop)
dispatcher.add_handler(stop_handler)

updater.start_polling()

# updater.start_webhook(listen=constants.INADDR_ANY, port=constants.PORT,
#                       url_path=constants.TOKEN, webhook_url=constants.URL + constants.TOKEN)
# updater.idle()
