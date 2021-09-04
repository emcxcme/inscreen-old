import constants
import data
import datetime
import helper
import math
import time
import queue_manager
from telegram.error import BadRequest
from telegram.ext import Updater
from telegram.files.inputmedia import InputMediaPhoto
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup


class Callback:
    def __init__(self, config):
        self.target_user_id = config.target_id[0]
        self.target_group_id = config.target_id[1]
        self.group_ids = config.group_ids
        self.group_titles = config.group_titles
        self.group_snumbers = config.group_snumbers
        self.qm = queue_manager.QueueManager(config.token[1:])
        self.ismasterclearable = False

    def nofollow(self, update, context):
        current_id = str(update.effective_chat.id)

        if current_id == self.target_user_id:
            # DO NOTHING
            return

        if current_id == self.target_group_id:
            # DO NOTHING
            return

        if current_id in self.group_ids:
            current_title = update.effective_chat.title
            keyboard = [
                [KeyboardButton("/nofollow"), KeyboardButton("/info")],
                [KeyboardButton("/clear"), KeyboardButton("/help")]
            ]
            markup = ReplyKeyboardMarkup(keyboard)

            if current_title not in data.group_titles_with_photo_ids:
                message = "Mag send po muna kayo ng picture."

                context.bot.send_message(
                    chat_id=current_id, text=message)

                message = "Ano pa pong maipaglilingkod ko?"

                context.bot.send_message(
                    chat_id=current_id, text=message, reply_markup=markup)
                time.sleep(constants.TIME_LIMIT * 2)

                return

            timestamp = datetime.datetime.now()
            time_template = timestamp.strftime("(%b %d, %Y) %A\n%I:%M:%S %p\n")
            photo_count = len(data.group_titles_with_photo_ids[current_title])

            message = time_template
            message += f"Forwarding {photo_count} screenshot/s.\n"
            message += "Please wait..."

            context.bot.send_message(chat_id=current_id, text=message)
            time.sleep(constants.TIME_LIMIT)

            photo_ids = []
            while len(data.group_titles_with_photo_ids[current_title]):
                photo_ids += [
                    data.group_titles_with_photo_ids[current_title].pop(0)]

                if len(photo_ids) == 10:
                    media_photos = list(map(InputMediaPhoto, photo_ids))

                    try:
                        Updater(token=self.qm.get_available_bot_token()).bot.send_media_group(
                            chat_id=self.target_group_id, media=media_photos)
                        self.qm.dequeue()

                        if current_title not in data.master_group_titles_with_photo_ids:
                            data.master_group_titles_with_photo_ids[current_title] = photo_ids
                        else:
                            data.master_group_titles_with_photo_ids[current_title] += photo_ids

                        photo_ids = []
                    except BadRequest as e:
                        print(e)

                        data.group_titles_with_photo_ids[current_title].extend(
                            photo_ids)

                        self.qm.dequeue()

                        photo_ids = []

            while photo_ids:
                media_photos = list(map(InputMediaPhoto, photo_ids))

                try:
                    Updater(token=self.qm.get_available_bot_token()).bot.send_media_group(
                        chat_id=self.target_group_id, media=media_photos)
                    self.qm.dequeue()

                    if current_title not in data.master_group_titles_with_photo_ids:
                        data.master_group_titles_with_photo_ids[current_title] = photo_ids
                    else:
                        data.master_group_titles_with_photo_ids[current_title] += photo_ids

                    photo_ids = []
                except BadRequest as e:
                    print(e)

                    self.qm.dequeue()

            data.group_titles_with_photo_ids.pop(current_title)

            message = f"{photo_count} screenshot/s forwared.\n\n"

            if current_title in data.group_titles_with_duplicate_photo_unique_id_count:
                duplicate_count = data.group_titles_with_duplicate_photo_unique_id_count[
                    current_title]

                message += f"{duplicate_count} duplicate files were detected thus ignored!!!" if duplicate_count > 1 else f"{duplicate_count} duplicate file was detected thus ignored!!!"

                data.master_photo_unique_ids |= {
                    *data.group_titles_with_photo_unique_ids[current_title]}

                data.group_titles_with_photo_unique_ids.pop(current_title)
                data.group_titles_with_duplicate_photo_unique_id_count.pop(
                    current_title)

            context.bot.send_message(
                chat_id=current_id, text=message)

            message = "Ano pa pong maipaglilingkod ko?"

            context.bot.send_message(
                chat_id=current_id, text=message, reply_markup=markup)
            time.sleep(constants.TIME_LIMIT * 2)

            helper.save()

    def info(self, update, context):
        current_id = str(update.effective_chat.id)

        if current_id == self.target_user_id:
            # DO NOTHING
            return

        if current_id == self.target_group_id:
            keyboard = [
                [KeyboardButton("/info"), KeyboardButton("/clear")]
            ]
            markup = ReplyKeyboardMarkup(keyboard)

            if len(data.master_group_titles_with_photo_ids) == 0:
                message = "Wala pa pong nagpasa.\n"

                context.bot.send_message(
                    chat_id=current_id, text=message)

                message = "Ano pa pong maipaglilingkod ko?"

                context.bot.send_message(
                    chat_id=current_id, text=message, reply_markup=markup)
                time.sleep(constants.TIME_LIMIT * 2)

                return

            if len(data.master_group_titles_with_photo_ids) != len(self.group_ids):
                groups_with_no_photo_ids = sorted(
                    set(constants.CONFIG.group_titles) - set(data.master_group_titles_with_photo_ids))

                puroks_with_no_content = [
                    "PUROK "+group.split("_")[-1]+"\n" for group in groups_with_no_photo_ids]

                message = "Hindi pa po kompleto.\n\n"
                message += "Mga hindi pa po nagpasa:\n"
                for purok in puroks_with_no_content:
                    message += purok

                context.bot.send_message(chat_id=current_id, text=message)
                time.sleep(constants.TIME_LIMIT)

            timestamp = datetime.datetime.now()
            time_template = timestamp.strftime("(%b %d, %Y) %A\n\n")

            message = "CFO Today Screenshots\n"
            message += time_template

            rankable = {}
            for purok in sorted(data.master_group_titles_with_photo_ids):
                purok_number = int(purok.split("_")[2])
                photo_count = len(
                    data.master_group_titles_with_photo_ids[purok])
                snumber_index = purok_number - 1
                snumber = int(self.group_snumbers[snumber_index])
                percentage = math.ceil((photo_count / snumber) * 100)

                message += f"PUROK {purok_number} - {percentage}% ({photo_count})\n"

                if percentage in rankable:
                    rankable[percentage] = [
                        f"{rankable[percentage][0]} & {purok_number}", f"{rankable[percentage][1]} & {photo_count}"]
                else:
                    rankable[percentage] = [purok, photo_count]

            total_photo_count = sum(
                list(map(len, data.master_group_titles_with_photo_ids.values())))
            total_snumber = sum(
                list(map(int, self.group_snumbers)))
            total_percentage = math.ceil(
                (total_photo_count / total_snumber) * 100)

            message += f"\nKabuuan = {total_percentage}% - {total_photo_count:,} views"

            context.bot.send_message(chat_id=current_id, text=message)
            time.sleep(constants.TIME_LIMIT)

            message = "CFO Today Leaderboards\n"
            message += time_template
            for idx, percentage in enumerate(sorted(rankable, reverse=True)):
                rank_number = idx + 1
                purok_number = rankable[percentage][0].split("_")[2]
                photo_count = rankable[percentage][1]

                message += f"{rank_number}) PUROK {purok_number} - {percentage}% ({photo_count})\n"
            message += f"\nKabuuan = {total_percentage}% - {total_photo_count:,} views"

            context.bot.send_message(
                chat_id=current_id, text=message)

            message = "Ano pa pong maipaglilingkod ko?"

            context.bot.send_message(
                chat_id=current_id, text=message, reply_markup=markup)
            time.sleep(constants.TIME_LIMIT * 2)

            return

        if current_id in self.group_ids:
            current_title = update.effective_chat.title
            keyboard = [
                [KeyboardButton("/nofollow"), KeyboardButton("/info")],
                [KeyboardButton("/clear"), KeyboardButton("/help")]
            ]
            markup = ReplyKeyboardMarkup(keyboard)

            timestamp = datetime.datetime.now()
            time_template = timestamp.strftime("(%b %d, %Y) %A\n\n")

            message = time_template
            message += "Screenshot Summary:\n\n"
            if current_title in data.group_titles_with_photo_ids and current_title in data.master_group_titles_with_photo_ids:
                message += "Meron na po kayong na i-send at na i-forward.\n\n"
            if current_title not in data.group_titles_with_photo_ids and current_title not in data.master_group_titles_with_photo_ids:
                message += "Wala pa po kayong na i-send at na i-forward.\n\n"
            if current_title in data.group_titles_with_photo_ids and current_title not in data.master_group_titles_with_photo_ids:
                message += "Meron na po kayong na i-send, pero wala pa po kayong na i-forward.\n\n"
            if current_title not in data.group_titles_with_photo_ids and current_title in data.master_group_titles_with_photo_ids:
                message += "Wala pa po kayong na i-send, pero meron na po kayong na i-forward.\n\n"

            current_group_index = None
            if current_title:
                current_group_index = self.group_titles.index(
                    current_title)
            snumber = int(self.group_snumbers[current_group_index])

            photo_count = 0
            if current_title in data.group_titles_with_photo_ids:
                photo_count = len(
                    data.group_titles_with_photo_ids[current_title])
                percentage = math.ceil((photo_count / snumber) * 100)

                message += f"Bilang ng na i-send: {photo_count}\nPorsyento ng na i-send: {percentage}%\n\n"

            master_photo_count = 0
            if current_title in data.master_group_titles_with_photo_ids:
                master_photo_count = len(
                    data.master_group_titles_with_photo_ids[current_title])
                master_percentage = math.ceil(
                    (master_photo_count / snumber) * 100)

                message += f"Bilang ng na i-forward: {master_photo_count}\nPorsyento ng na i-forward: {master_percentage}%\n\n"

            total_photo_count = photo_count + master_photo_count
            total_percentage = math.ceil(
                (total_photo_count / snumber) * 100)

            if current_title in data.group_titles_with_photo_ids and current_title in data.master_group_titles_with_photo_ids:
                message += f"Kabuuang bilang: {total_photo_count}\nKabuuang porsyento: {total_percentage}%\n\n"

            if current_title in data.group_titles_with_duplicate_photo_unique_id_count:
                duplicate_count = data.group_titles_with_duplicate_photo_unique_id_count[
                    current_title]

                message += f"{duplicate_count} duplicate files were detected thus ignored!!!" if duplicate_count > 1 else f"{duplicate_count} duplicate file was detected thus ignored!!!"

            context.bot.send_message(
                chat_id=current_id, text=message)

            message = "Ano pa pong maipaglilingkod ko?"

            context.bot.send_message(
                chat_id=current_id, text=message, reply_markup=markup)
            time.sleep(constants.TIME_LIMIT * 2)

    def clear(self, update, context):
        current_id = str(update.effective_chat.id)

        if current_id == self.target_user_id:
            self.ismasterclearable = not self.ismasterclearable

            print(f"Master clearable is set to {self.ismasterclearable}")

            return

        if current_id == self.target_group_id:
            keyboard = [
                [KeyboardButton("/info"), KeyboardButton("/clear")]
            ]
            markup = ReplyKeyboardMarkup(keyboard)

            message = "Disabled."

            if self.ismasterclearable:
                data.master_group_titles_with_photo_ids = {}

                message = "Cleared all queries."

            self.ismasterclearable = False

            context.bot.send_message(
                chat_id=current_id, text=message)

            message = "Ano pa pong maipaglilingkod ko?"

            context.bot.send_message(
                chat_id=current_id, text=message, reply_markup=markup)
            time.sleep(constants.TIME_LIMIT * 2)

            helper.save()

            return

        if current_id in self.group_ids:
            current_title = update.effective_chat.title
            message = ""
            keyboard = [
                [KeyboardButton("/nofollow"), KeyboardButton("/info")],
                [KeyboardButton("/clear"), KeyboardButton("/help")]
            ]
            markup = ReplyKeyboardMarkup(keyboard)

            if current_title in data.group_titles_with_photo_unique_ids:
                data.group_titles_with_photo_unique_ids.pop(current_title)

            if current_title in data.group_titles_with_duplicate_photo_unique_id_count:
                data.group_titles_with_duplicate_photo_unique_id_count.pop(
                    current_title)

            if current_title in data.group_titles_with_photo_ids:
                data.group_titles_with_photo_ids.pop(current_title)

                message += "Cleared current queries."
            else:
                message += "Query is already empty."

            context.bot.send_message(
                chat_id=current_id, text=message)

            message = "Ano pa pong maipaglilingkod ko?"

            context.bot.send_message(
                chat_id=current_id, text=message, reply_markup=markup)
            time.sleep(constants.TIME_LIMIT * 2)

            helper.save()

    def help(self, update, context):
        current_id = str(update.effective_chat.id)

        if current_id == self.target_user_id:
            # DO NOTHING
            return

        if current_id == self.target_group_id:
            # DO NOTHING
            return

        if current_id in self.group_ids:
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
            keyboard = [
                [KeyboardButton("/nofollow"), KeyboardButton("/info")],
                [KeyboardButton("/clear"), KeyboardButton("/help")]
            ]
            markup = ReplyKeyboardMarkup(keyboard)

            context.bot.send_message(
                chat_id=current_id, text=message)

            message = "Ano pa pong maipaglilingkod ko?"

            context.bot.send_message(
                chat_id=current_id, text=message, reply_markup=markup)
            time.sleep(constants.TIME_LIMIT * 2)

    def received_photo(self, update, context):
        current_id = str(update.effective_chat.id)

        if current_id == self.target_user_id:
            # DO NOTHING
            return

        if current_id == self.target_group_id:
            # DO NOTHING
            return

        if current_id in self.group_ids:
            current_title = update.effective_chat.title
            current_photo_id = update.message.photo[-1].file_id
            current_photo_unique_id = update.message.photo[-1].file_unique_id

            if current_photo_unique_id in data.master_photo_unique_ids or current_title in data.group_titles_with_photo_unique_ids and current_photo_unique_id in data.group_titles_with_photo_unique_ids[current_title]:
                message = "Duplicate has been found and ignored.\n"
                message += f"File unique id: {current_photo_unique_id}"

                print(message)

                if current_title in data.group_titles_with_duplicate_photo_unique_id_count:
                    data.group_titles_with_duplicate_photo_unique_id_count[current_title] += 1

                    return

                data.group_titles_with_duplicate_photo_unique_id_count[current_title] = 1

                return

            if current_title in data.group_titles_with_photo_unique_ids:
                data.group_titles_with_photo_unique_ids[current_title] += [
                    current_photo_unique_id]
            else:
                data.group_titles_with_photo_unique_ids[current_title] = [
                    current_photo_unique_id]

            if current_title in data.group_titles_with_photo_ids:
                data.group_titles_with_photo_ids[current_title] += [
                    current_photo_id]

                helper.save()

                return

            data.group_titles_with_photo_ids[current_title] = [
                current_photo_id]

            helper.save()
