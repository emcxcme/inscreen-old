import logging
import datetime
import time
from telegram.ext import MessageHandler, Filters, Updater
from telegram.ext import CommandHandler
from telegram.files.inputmedia import InputMediaPhoto

updater = Updater(
    token='', use_context=True)
dispatcher = updater.dispatcher

media_photo_group = {}
target_group = 0

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def nofollow(update, context):
    if update.effective_chat.id == target_group:
        return
    global media_photo_group
    if update.effective_chat.id not in media_photo_group:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Send pic muna lods.")
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Please wait...")
    timestamp = str(datetime.datetime.now())
    text_info = "Date And Time: " + timestamp + "\n"
    if update.effective_chat.id in media_photo_group:
        text_info += "Image Count: " + \
            str(len(media_photo_group[update.effective_chat.id])) + "\n"
    else:
        text_info += "Image Count: 0\n"
    text_info += "Purok: " + update.effective_chat.title.split("_")[-1]
    context.bot.send_message(
        chat_id=target_group, text=text_info)
    group = []
    photo_count = len(media_photo_group[update.effective_chat.id])
    for counter in range(photo_count):
        group += [media_photo_group[update.effective_chat.id].pop(0)]
        if(len(group) == 10):
            context.bot.send_media_group(
                chat_id=target_group, media=group)
            group = []
            time.sleep(30)
    context.bot.send_media_group(
        chat_id=target_group, media=group)
    media_photo_group.pop(update.effective_chat.id)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Image forwarded.")
    time.sleep(5)


def info(update, context):
    if update.effective_chat.id == target_group:
        return
    timestamp = str(datetime.datetime.now())
    text_info = "Date And Time: " + timestamp + "\n"
    if update.effective_chat.id in media_photo_group:
        text_info += "Image Count: " + \
            str(len(media_photo_group[update.effective_chat.id])) + "\n"
    else:
        text_info += "Image Count: 0\n"
    text_info += "Purok: " + update.effective_chat.title.split("_")[-1]
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text_info)


def help(update, context):
    if update.effective_chat.id == target_group:
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Pindutin ang /nofollow para mai-forward na po kay Ka. Wilmer. Salamat po.")


def echo_text(update, context):
    if update.effective_chat.id == target_group:
        return
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Invalid command. Press /help.")


def echo_photo(update, context):
    if update.effective_chat.id == target_group:
        return
    global media_photo_group
    if update.effective_chat.id in media_photo_group:
        media_photo_group[update.effective_chat.id].append(
            InputMediaPhoto(update.message.photo[-1]))
    else:
        media_photo_group[update.effective_chat.id] = [
            InputMediaPhoto(update.message.photo[-1])]


nofollow_handler = CommandHandler('nofollow', nofollow)
dispatcher.add_handler(nofollow_handler)

info_handler = CommandHandler('info', info)
dispatcher.add_handler(info_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

echo_photo_handler = MessageHandler(Filters.attachment, echo_photo)
dispatcher.add_handler(echo_photo_handler)

echo_text_handler = MessageHandler(Filters.text, echo_text)
dispatcher.add_handler(echo_text_handler)

updater.start_polling()
