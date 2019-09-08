import os
import torch
import torch.nn.functional as F
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
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
    update.message.reply_text(messages.start_message)
    return constants.LOGIN


def set_student_number(bot, update, user_data):
    update.message.reply_text(messages.password_message)
    username = update.message.text
    user_data['username'] = username
    return constants.PASSWORD


def set_student_password(bot, update, user_data):
    password = update.message.text
    username = user_data['username']
    chat_id = update.message.chat_id

    try:
        grades_data = get_semester_data(username, password)
        user_data['semester_data'] = grades_data
        # takes user image's feature vector
        user_info = get_user_info(username, password)
        user_data['feature'] = user_info['feature']
        user_data['name_surname'] = user_info['name_surname']
        user_data['program'] = user_info['program']
        user_data['chat_id'] = chat_id
        encrypted_password = encryptor.encrypt(password)
        user_data['password'] = encrypted_password
        database.insert_user(user_data)
        send_message(bot, chat_id, messages.done_message)
    except ValueError:
        send_message(bot, chat_id, messages.incorrect_data_message)
        return constants.LOGIN
    return ConversationHandler.END


def notify_grades(bot_):
    while True:

        for user in database.collection.find():
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
    update.message.reply_text('Send me photo of person you want to find')
    return constants.PHOTO


def find_user(bot, update):
    chat_id = update.message.chat_id
    photo_file = update.message.photo[-1].get_file()
    file_path = chat_id + 'jpg'
    photo_file.download(file_path)
    current_image = Image.open(file_path).convert('RGB')

    answer_feature = get_feature(current_image)
    if not isinstance(answer_feature, torch.Tensor):
        if answer_feature == -1:
            send_message(bot, chat_id, messages.no_face_message)
            return ConversationHandler.END
        if answer_feature == -2:
            send_message(bot, chat_id, messages.more_than_one_message)
            return ConversationHandler.END
    max_sim = 0
    for user in database.collection.find():
        if 'feature' not in user:
            continue
        user_vector = torch.tensor(user['feature'])
        similarity = F.cosine_similarity(answer_feature, user_vector)
        if similarity > max_sim:
            max_sim = similarity
            needed_user = user
    if max_sim.item() < constants.THRESHOLD_SIMILARITY:
        update.message.reply_text(messages.not_subscribed_message)
    update.message.reply_text(f'this is {needed_user["name_surname"]} from {needed_user["program"]} , sim = {max_sim}')

    os.remove(file_path)
    return ConversationHandler.END


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

    # thread = threading.Thread(target=notify_grades, args=(updater.bot,))
    # thread.start()

    enter_conversation = ConversationHandler(

        entry_points=[CommandHandler('start', start)],

        states={
            constants.LOGIN: [MessageHandler(Filters.text, set_student_number, pass_user_data=True)],
            constants.PASSWORD: [MessageHandler(Filters.text, set_student_password, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]

    )
    photo_conversation = ConversationHandler(

        entry_points=[CommandHandler('find_user', find_user_start)],

        states={
            constants.PHOTO: [MessageHandler(Filters.photo, find_user)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]

    )
    dp.add_handler(enter_conversation)
    dp.add_handler(photo_conversation)
    updater.start_polling()


def send_message(bot, chat_id, send_text):
    try:
        bot.send_message(chat_id=chat_id, text=send_text, parse_mode='HTML')
    except BadRequest:
        print('No such chat id')


def send_photo(bot, chat_id, file_path):
    try:
        bot.send_photo(chat_id=chat_id, photo=open(file_path, 'rb'), pasre_mode='HTML')
    except BadRequest:
        print('No such chat id')


if __name__ == '__main__':
    main()
