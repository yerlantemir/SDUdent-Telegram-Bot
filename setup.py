import os
import threading
import torch
import torch.nn.functional as F
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.error import BadRequest
from PIL import Image
from parser import get_semester_data, get_user_info
from Facade import BotFacade
from model.utils import get_feature
import AESencoder as encryptor
import constants
import database
import messages


def start(bot, update):
    reply_keyboard = [['CANCEL']]
    update.message.reply_text(messages.start_message,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True))
    return constants.LOGIN


def set_student_number(bot, update, user_data):
    user_text = update.message.text
    if user_text == 'CANCEL':
        return ConversationHandler.END
    update.message.reply_text(messages.password_message)
    username = user_text
    user_data['username'] = username
    return constants.PASSWORD


def set_student_password(bot, update, user_data):
    password = update.message.text
    username = user_data['username']
    chat_id = update.message.chat_id
    reply_keyboard = [['Yes', 'No']]
    send_message(bot, chat_id, messages.wait_message)
    try:
        grades_data = get_semester_data(username, password)
        user_data['semester_data'] = grades_data
        # takes user image's feature vector
        user_info = get_user_info(username, password)
        user_data['chat_id'] = chat_id
        encrypted_password = encryptor.encrypt(password)
        user_data['password'] = encrypted_password
        database.insert_user(user_data, user_info)
        send_message(bot, chat_id, messages.done_message,
                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return constants.ASK_DATA
    except ValueError:
        send_message(bot, chat_id, messages.incorrect_data_message)
        return constants.LOGIN


def ask_data(bot, update):
    chat_id = update.message.chat_id
    info_allow_state = update.message.text
    if info_allow_state == "Yes":
        info_allow_state = True
    else:
        info_allow_state = False
    database.change_state(chat_id, info_allow_state)
    current_state = 'Enabled' if info_allow_state else 'Disabled'
    update.message.reply_text('Your info ' + current_state + '!', reply_markup=ReplyKeyboardRemove())


def notify_grades(bot_):
    while True:

        for user in database.collection_grades.find():
            old_grades = user['semester_data']
            chat_id = user['chat_id']

            encrypted_username = user['username']
            encrypted_password = encryptor.decrypt(user['password'])
            new_grades = get_new_grades(encrypted_username, encrypted_password)

            if new_grades is None:
                print('CHANGED DATA', encrypted_username, encrypted_password)
                continue

            something_changed = False
            for subject_name, grades in new_grades.items():
                # RARE situation when user changed his subject
                if subject_name not in old_grades:
                    continue

                differences = grades.items() - old_grades[subject_name].items()
                for difference in differences:
                    something_changed = True
                    # difference ex : ('average' :'85')
                    changed_state = difference[0]  # difference[0] => 'average'
                    changed_value = difference[1]  # difference[1] => '85'
                    prev_value = old_grades[subject_name][changed_state]
                    send_message(bot_, chat_id, f'{changed_state} by subject {subject_name} '
                                                f'was changed from {prev_value} to {changed_value}')

            if something_changed:
                database.update_grades(chat_id, new_grades)


def get_new_grades(encrypted_username, encrypted_password):
    try:
        return get_semester_data(encrypted_username, encrypted_password)
    except BadRequest:
        return None


def find_user_start(bot, update):
    reply_keyboard = [['CANCEL']]
    update.message.reply_text(messages.send_photo_message,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True))
    return constants.PHOTO


def find_user(bot, update):
    if update.message.text == 'CANCEL':
        return ConversationHandler.END

    chat_id = update.message.chat_id
    photo_file = update.message.photo[-1].get_file()
    file_path = str(chat_id) + 'jpg'
    photo_file.download(file_path)
    current_image = Image.open(file_path).convert('RGB')
    current_picture_feature = get_feature(current_image)
    if not isinstance(current_picture_feature, torch.Tensor):
        # no face detected
        if current_picture_feature == -1:
            return remove_file_and_stop_conversation(update, messages.no_face_message, file_path=file_path)
        # more than one face was detected
        if current_picture_feature == -2:
            return remove_file_and_stop_conversation(update, messages.more_than_one_message, file_path=file_path)

    send_message(bot, chat_id, messages.wait_searching_message, reply_markup=ReplyKeyboardRemove())
    needed_user, max_sim = get_needed_user(current_picture_feature)

    if max_sim.item() < constants.THRESHOLD_SIMILARITY:
        return remove_file_and_stop_conversation(update, messages.not_subscribed_message, file_path=file_path)

    if 'info_allow_state' not in needed_user or not needed_user['info_allow_state']:
        return remove_file_and_stop_conversation(update, messages.disabled_info_message, file_path=file_path)

    text = messages.found_message(needed_user['name_surname'], needed_user['program'], max_sim)
    return remove_file_and_stop_conversation(update, text, file_path=file_path)


def get_needed_user(current_picture_feature):
    max_sim = 0

    for user in database.collection_features.find():

        if 'feature' not in user:
            continue

        user_vector = torch.tensor(user['feature'])
        similarity = F.cosine_similarity(current_picture_feature, user_vector)

        if similarity > max_sim:
            max_sim = similarity
            needed_user = user

    return needed_user, max_sim


def remove_file_and_stop_conversation(update, text, file_path):
    update.message.reply_text(text)
    os.remove(file_path)
    return ConversationHandler.END


def change_state(bot, update):
    chat_id = update.message.chat_id

    prev_state = database.find_by_chat_id(chat_id)['info_allow_state']
    database.change_state(chat_id, not prev_state)
    current_state = 'Disabled' if prev_state else 'Enabled'
    current_state2 = 'Enable' if prev_state else 'Disable'
    update.message.reply_text('Info ' + current_state + '! Call this command again to ' + current_state2)


def feedback_start(bot, update):
    reply_keyboard = [['CANCEL']]
    update.message.reply_text(messages.feedback_start_message,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True))
    return constants.FEEDBACK


def save_feedback(bot, update):
    feedback_text = update.message.text
    if feedback_text == 'CANCEL':
        return ConversationHandler.END
    chat_id = update.message.chat_id
    database.add_feedback(chat_id, feedback_text)
    update.message.reply_text(messages.thanks_message)


def cancel(bot, update):
    return ConversationHandler.END


def unknown_command(bot, update):
    send_message(bot, update.message.chat_id, messages.what_message)


def help_call(bot, update):
    chat_id = update.message.chat_id
    send_message(bot, chat_id, messages.help_message)


def main():
    facade = BotFacade()
    updater = facade.getBot()
    dp = updater.dispatcher

    thread = threading.Thread(target=notify_grades, args=(updater.bot,))
    thread.start()

    enter_conversation = ConversationHandler(

        entry_points=[CommandHandler('start', start)],

        states={
            constants.LOGIN: [MessageHandler(Filters.text, set_student_number, pass_user_data=True)],
            constants.PASSWORD: [MessageHandler(Filters.text, set_student_password, pass_user_data=True)],
            constants.ASK_DATA: [MessageHandler(Filters.regex('^(Yes|No)$'), ask_data)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]

    )
    photo_conversation = ConversationHandler(

        entry_points=[CommandHandler('find_user', find_user_start)],

        states={
            constants.PHOTO: [MessageHandler(Filters.photo | Filters.text, find_user)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]

    )
    feedback_handler = ConversationHandler(

        entry_points=[CommandHandler('feedback', feedback_start)],

        states={
            constants.FEEDBACK: [MessageHandler(Filters.text, save_feedback)],

            constants.PHOTO: [MessageHandler(Filters.photo, find_user, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]

    )
    change_state_handler = CommandHandler('change_state', change_state)
    dp.add_handler(enter_conversation)
    dp.add_handler(photo_conversation)
    dp.add_handler(change_state_handler)
    dp.add_handler(feedback_handler)
    updater.start_polling()


def send_message(bot, chat_id, send_text, reply_markup=None):
    try:
        bot.send_message(chat_id=chat_id, text=send_text, parse_mode='HTML', reply_markup=reply_markup)
    except BadRequest:
        print('No such chat id')


def send_photo(bot, chat_id, file_path):
    try:
        bot.send_photo(chat_id=chat_id, photo=open(file_path, 'rb'), pasre_mode='HTML')
    except BadRequest:
        print('No such chat id')


if __name__ == '__main__':
    main()
