import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler,MessageHandler,Filters,ConversationHandler
import datetime
import secret_data as sd
import scrapper
from selenium.common.exceptions import NoSuchElementException

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

username = ''
password = ''

USERNAME,PASSWORD,GENDER = range(3)

weekdays = {}


def callback_get_time(bot,update):
 
    date = update.message.date
    time = datetime.time(date.hour,date.minute,date.second)
    weekday = date.isoweekday()
    days = 0
    
    if(weekday >= 6):
        days = 8-weekday
        weekday = 1

    indexOfMin = closest_index(time,weekday)
    
    if days > 0:

        indexOfMin = 0

    next_lesson = weekdays[weekday][indexOfMin]
    next_lesson_time = next_lesson.time
    
    next_lesson_date = datetime.datetime(date.year,
    date.month,date.day+days,next_lesson_time.hour,next_lesson_time.minute,00)

    bot.send_message(chat_id = update.message.chat_id , 
            text = 'Your next lesson is {}\nWhere?{}\nTeacher:{} \nuntil lesson:{}'.format(next_lesson.title,next_lesson.room,
                next_lesson.teacher_name,next_lesson_date - date))

    
    

def closest_index(time,weekday):
    my_time_minutes = time.hour*60 + time.minute
    min = 24*60
    indexOfMin = 0

    global weekdays
    for i in range(len(weekdays[weekday])):
        
        subject_time = weekdays[weekday][i].time
        minutes = subject_time.hour*60+subject_time.minute
        difference = minutes - my_time_minutes 

        if(difference < min and difference > 0):
            min = difference
            indexOfMin = i
        

    return indexOfMin




def start(bot,update):
    update.message.reply_text('Enter your login:')

    return USERNAME
    


def get_username(bot,update):
    
    global username
    username = update.message.text
    update.message.reply_text('Now,enter your password:')
    
    return PASSWORD


def get_password(bot,update):

    global password
    password = update.message.text
    update.message.reply_text('Wait about 10 seconds,we are getting data from portal')

    try:
    
        schedule = scrapper.Schedule(username,password)

    except NoSuchElementException:
        print('kek')
        update.message.reply_text('Your entered incorrect data,try again:')
        update.message.reply_text('Enter your login:')
        
        return USERNAME

    global weekdays
    weekdays = schedule.get_schedule_data()

    update.message.reply_text('Your are welcome,now you can use our bot!')
    
    
    return 

def cancel(bot,update):
    
    return ConversationHandler.END


def main():

    TOKEN = sd.get_token()

    updater = Updater(token = TOKEN)
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            
            USERNAME: [MessageHandler(Filters.text, get_username)],

            PASSWORD: [MessageHandler(Filters.text, get_password)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
   

    dp.add_handler(CommandHandler('next',callback_get_time))
    dp.add_handler(conv_handler)    
    updater.start_polling()


if __name__ == '__main__':
    main()