import datetime
import helper
import pickle
import logging
import math
import os
import sys
import telegram
import time
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram.files.inputmedia import InputMediaPhoto

config_filename = "inscreen_config.txt"
config = helper.parse_config(config_filename)
TOKEN = config.token[0]
PORT = int(os.environ.get("PORT", "8443"))

bot = telegram.Bot(token=TOKEN)
# bot.setWebhook("https://morning-harbor-80510.herokuapp.com/"+TOKEN)

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

master_group_titles_with_photos = {}
group_titles_with_photos = {}

with open("data.pkl", "rb") as file:
    master_group_titles_with_photos, group_titles_with_photos = pickle.load(
        file)
time.sleep(5)

safe_mode = True


def nofollow(update, context):
    global master_group_titles_with_photos
    global group_titles_with_photos
    current_id = str(update.effective_chat.id)
    target_id = config.target_id[0]
    group_ids = config.group_ids
    timestamp = datetime.datetime.now()
    if current_id == target_id:
        # DO NOTHING
        return
    if current_id in group_ids:
        current_title = update.effective_chat.title
        if current_title not in group_titles_with_photos:
            message = "Mag send po muna kayo ng picture."
            context.bot.send_message(chat_id=current_id, text=message)
            if(safe_mode):
                time.sleep(4)
            return
        time_template = timestamp.strftime("(%b %d, %Y) %A\n%I:%M:%S %p\n")
        photo_count = len(group_titles_with_photos[current_title])
        message = time_template
        message += f"Forwarding {photo_count} screenshot/s.\n"
        message += "Please wait..."
        context.bot.send_message(chat_id=current_id, text=message)
        if(safe_mode):
            time.sleep(4)
        photo_group = []
        for counter in range(photo_count):
            photo_group += [group_titles_with_photos[current_title].pop(0)]
            if current_title not in master_group_titles_with_photos:
                master_group_titles_with_photos[current_title] = [photo_group]
            else:
                master_group_titles_with_photos[current_title].append(
                    photo_group)
            if len(photo_group) == 10:
                photo_group = list(map(InputMediaPhoto, photo_group))
                context.bot.send_media_group(
                    chat_id=target_id, media=photo_group)
                photo_group = []
                time.sleep(30)
        if photo_group:
            photo_group = list(map(InputMediaPhoto, photo_group))
            context.bot.send_media_group(chat_id=target_id, media=photo_group)
        if(safe_mode):
            time.sleep(3 * len(photo_group))
        message = f"{photo_count} screenshot/s forwared."
        group_titles_with_photos.pop(current_title)
        context.bot.send_message(chat_id=current_id, text=message)
        with open("data.pkl", "wb") as file:
            pickle.dump([master_group_titles_with_photos,
                        group_titles_with_photos], file, protocol=pickle.HIGHEST_PROTOCOL)
        if(safe_mode):
            time.sleep(4)


def info(update, context):
    global group_titles_with_photos
    global master_group_titles_with_photos
    current_id = str(update.effective_chat.id)
    target_id = config.target_id[0]
    group_ids = config.group_ids
    group_titles = config.group_titles
    timestamp = datetime.datetime.now()
    if current_id == target_id:
        if len(master_group_titles_with_photos) == 0:
            message = "Wala pa pong nagpasa.\n"
            context.bot.send_message(chat_id=current_id, text=message)
            if(safe_mode):
                time.sleep(4)
            return
        if len(master_group_titles_with_photos) != len(group_ids):
            groups_no_photo = sorted(
                set(group_titles) - set(master_group_titles_with_photos))
            groups_no_photo = [
                "PUROK "+group.split("_")[-1]+"\n" for group in groups_no_photo]
            message = "Hindi pa po kompleto.\n\n"
            message += "Mga hindi pa po nagpasa:\n"
            for group in groups_no_photo:
                message += group
            context.bot.send_message(chat_id=current_id, text=message)
            if(safe_mode):
                time.sleep(4)
        time_template = timestamp.strftime("(%b %d, %Y) %A\n\n")
        message = "CFO Today Screenshots\n"
        message += time_template
        total_photo_count = 0
        total_snumber = sum(list(map(int, config.group_snumbers)))
        rankable = {}
        for purok in sorted(master_group_titles_with_photos):
            purok_number = int(purok.split("_")[2])
            photo_count = len(master_group_titles_with_photos[purok])
            total_photo_count += photo_count
            snumber_index = purok_number - 1
            snumber = int(config.group_snumbers[snumber_index])
            percentage = math.ceil((photo_count / snumber) * 100)
            rankable[percentage] = [purok, photo_count]
            message += f"PUROK {purok_number} - {percentage}% ({photo_count})\n"
        total_percentage = math.ceil((total_photo_count / total_snumber) * 100)
        message += f"\nKabuuan = {total_percentage}% - {total_photo_count:,} views"
        context.bot.send_message(chat_id=current_id, text=message)
        if(safe_mode):
            time.sleep(4)
        message = "CFO Today Leaderboards\n"
        message += time_template
        for idx, percentage in enumerate(sorted(rankable)):
            rank_number = idx + 1
            photo_count = rankable[percentage][1]
            purok_number = rankable[percentage][0].split("_")[2]
            message += f"{rank_number}) PUROK {purok_number} - {percentage}% ({photo_count})"
        context.bot.send_message(chat_id=current_id, text=message)
        if(safe_mode):
            time.sleep(4)
        return
    if current_id in group_ids:
        current_title = update.effective_chat.title
        time_template = timestamp.strftime("(%b %d, %Y) %A\n%I:%M:%S %p\n\n")
        current_group_index = config.group_titles.index(
            current_title) if current_title else None
        snumber = int(config.group_snumbers[current_group_index])
        message = time_template
        message += "Screenshot Summary:\n\n"
        if current_title in group_titles_with_photos and current_title in master_group_titles_with_photos:
            message += "Meron na po kayong na i-send at na i-forward.\n\n"
        if current_title not in group_titles_with_photos and current_title not in master_group_titles_with_photos:
            message += "Wala pa po kayong na i-send at na i-forward.\n\n"
        if current_title in group_titles_with_photos and current_title not in master_group_titles_with_photos:
            message += "Meron na po kayong na i-send, pero wala pa po kayong na i-forward.\n\n"
        if current_title not in group_titles_with_photos and current_title in master_group_titles_with_photos:
            message += "Wala pa po kayong na i-send, pero meron na po kayong na i-forward.\n\n"
        if current_title in group_titles_with_photos:
            photo_count = len(group_titles_with_photos[current_title])
            percentage = math.ceil((photo_count / snumber) * 100)
            message += f"Bilang: {photo_count}\nPorsyento: {percentage}%\n"
        if current_title in master_group_titles_with_photos:
            master_photo_count = len(
                master_group_titles_with_photos[current_title])
            master_percentage = math.ceil((master_photo_count / snumber) * 100)
            message += f"Bilang ng na i-forward: {master_photo_count}\nPorsyento ng na i-forward: {master_percentage}%"
        context.bot.send_message(chat_id=current_id, text=message)
        if(safe_mode):
            time.sleep(4)


def clear(update, context):
    global master_group_titles_with_photos
    global group_titles_with_photos
    current_id = str(update.effective_chat.id)
    target_id = config.target_id[0]
    group_ids = config.group_ids
    if current_id == target_id:
        master_group_titles_with_photos = {}
        message = "Cleared all queries."
        context.bot.send_message(chat_id=current_id, text=message)
        with open("data.pkl", "wb") as file:
            pickle.dump([master_group_titles_with_photos,
                        group_titles_with_photos], file, protocol=pickle.HIGHEST_PROTOCOL)
        if(safe_mode):
            time.sleep(4)
        return
    if current_id in group_ids:
        current_title = update.effective_chat.title
        message = ""
        if current_title in group_titles_with_photos:
            group_titles_with_photos.pop(current_title)
            message += "Cleared current queries."
        else:
            message += "Query is already empty."
        context.bot.send_message(chat_id=current_id, text=message)
        with open("data.pkl", "wb") as file:
            pickle.dump([master_group_titles_with_photos,
                        group_titles_with_photos], file, protocol=pickle.HIGHEST_PROTOCOL)
        if(safe_mode):
            time.sleep(4)


def help(update, context):
    current_id = str(update.effective_chat.id)
    target_id = config.target_id[0]
    group_ids = config.group_ids
    if current_id == target_id:
        return
    if current_id in group_ids:
        message = """
Mga kapatid, ito po ang mga hakbang sa pag-send ng screenshot:

1) Mag-send po ng mga screenshot.
2) Pindutin po ang /nofollow.

*Ang mga command ay makikita po sa pagpindot ng slash na naka kahon sa gilid po ng message bar.*
        
Kung magkamali naman, ay pindutin lamang po ang /clear upang hindi po mabilang sa maifo-forward ang mga larawan na hindi pa po nai-/nofollow.

*Tandaan na pag pindot po ng /clear ay mawawala po ang lahat ng puwedeng mai-/nofollow. Kaya lahat po ng hindi pa nai-/nofollow na larawan, ay i-send pong muli upang mapabilang sa maino-/nofollow*

*Ang lahat po ng nai-/nofollow ay mananatili pong nai-forward kay Ka Wilmer at mapapasama sa bilang ng mga na ipasa, kaya huwag po ninyong kakalimutang mag /nofollow*
        

Ito naman po ang mga bilin sa pagpapadala ng larawan:

Bago po ang 10PM ay naka pag-send at /nofollow na. Hangga't maari, 9:30PM pa lamang, ay nagawa na po iyon para hindi po kayo nagsasabay-sabay nang pag-send at pag-/nofollow ng mga screenshot.

Tiyakin lamang na screenshot po ang nai-send at maino-/nofollow. Ngunit kung kayo po ay nagkamali, pindutin lamang ang /clear at saka i-send po ulit at i-/nofollow.

*Agahan po ang pag send at pag-/nofollow. Puwede pong kahit kailan at kahit ilang beses po kayo mag-/nofollow. Puwede rin pong utay-utayin ang pag send; Halimbawa: May nag-send na po sa inyo, puwede niyo na pong i-send yun dito at saka pindutin ang /nofollow*

*Huwag niyo na pong bilangin ang screenshot, pero kung gusto po ninyong malaman kung ilan na po ang nai-send ninyo; pindutin po lamang ang /info*

Salamat po!
"""
        context.bot.send_message(chat_id=current_id, text=message)
        if(safe_mode):
            time.sleep(4)


def stop(update, context):
    global master_group_titles_with_photos
    global group_titles_with_photos
    current_id = str(update.effective_chat.id)
    target_id = str(config.target_id[-1])
    group_ids = config.group_ids
    if current_id == target_id:
        print("Saving data...")
        with open("data.pkl", "wb") as file:
            pickle.dump([master_group_titles_with_photos, group_titles_with_photos],
                        file, protocol=pickle.HIGHEST_PROTOCOL)
        print("Bye!")
        updater.stop()
        sys.exit()
    if current_id in group_ids:
        message = "You don't have access."
        context.bot.send_message(chat_id=current_id, text=message)


def received_photo(update, context):
    global master_group_titles_with_photos
    global group_titles_with_photos
    current_id = str(update.effective_chat.id)
    target_id = config.target_id[0]
    group_ids = config.group_ids
    if current_id == target_id:
        # DO NOTHING
        return
    if current_id in group_ids:
        current_title = update.effective_chat.title
        current_photo = update.message.photo[-1].file_id
        if current_title in group_titles_with_photos:
            group_titles_with_photos[current_title].append(current_photo)
            with open("data.pkl", "wb") as file:
                pickle.dump([master_group_titles_with_photos,
                            group_titles_with_photos], file, protocol=pickle.HIGHEST_PROTOCOL)
            return
        group_titles_with_photos[current_title] = [current_photo]
        with open("data.pkl", "wb") as file:
            pickle.dump([master_group_titles_with_photos,
                        group_titles_with_photos], file, protocol=pickle.HIGHEST_PROTOCOL)


# def received_text(update, context):
#     current_id = str(update.effective_chat.id)
#     target_id = config.target_id[0]
#     group_ids = config.group_ids
#     if current_id == target_id:
#         return
#     if current_id in group_ids:
#         return


nofollow_handler = CommandHandler("nofollow", nofollow)
dispatcher.add_handler(nofollow_handler)

info_handler = CommandHandler("info", info)
dispatcher.add_handler(info_handler)

clear_handler = CommandHandler("clear", clear)
dispatcher.add_handler(clear_handler)

help_handler = CommandHandler("help", help)
dispatcher.add_handler(help_handler)

stop_handler = CommandHandler("stop", stop)
dispatcher.add_handler(stop_handler)

received_photo_handler = MessageHandler(Filters.photo, received_photo)
dispatcher.add_handler(received_photo_handler)

# received_text_handler = MessageHandler(Filters.text, received_text)
# dispatcher.add_handler(received_text_handler)

updater.start_polling()

# updater.start_webhook(listen="0.0.0.0", port=PORT,
#                       url_path=TOKEN, webhook_url="https://morning-harbor-80510.herokuapp.com/"+TOKEN)
# updater.idle()
