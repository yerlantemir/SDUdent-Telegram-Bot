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


weekdays = {}







def start(bot,update):
    
    update.message.reply_text('Welcome to our bot!')


def set_username(bot,update,args):

    global username
    
    try:
    
        username = args[0]
    
    except IndexError:

        update.message.reply_text('Your foggot to enter your login(example: /set_username 170103024),please,try again')
        return
    
    update.message.reply_text('Username saved')


def set_password(bot,update,args):
    
    global password
    try:
        password = args[0]
    except IndexError:

        update.message.reply_text('Your foggot to enter your password(example: /set_password 170103024),please,try again')
        return
    
    update.message.reply_text('Password saved')
    

def save_schedule(bot,update):
    
    global username,password,weekdays
    
    if(username == '' or password == ''):

        update.message.reply_text('You did not entered your login or password,please,firtsly use /set_username and /set_password methods')
        return

    update.message.reply_text('We are getting data from portal,wait about 10 seconds')
    
    try:
        schedule = scrapper.Schedule(username,password)
    
    except NoSuchElementException:

        update.message.reply_text('Your entered incorrect username/password,so we could not get your schedule,try again!')
        return
    
    weekdays = schedule.get_schedule_data()
    update.message.reply_text('We got your schedule,you are welcome to use!')


def get_schedule(bot,update,args):
    
    try:
        
        day = int(args[0])

    except IndexError:
        
        update.message.reply_text('Your foggot to enter day(example: /get_schedule 2 ,to get tuesday\'s schedule),please,try again')
        return
    
    global weekdays

    for i in range(len(weekdays[day])):
        update.message.reply_text('{}){}'.format(i+1,weekdays[day][i]))




def main():

    TOKEN = sd.get_token()

    updater = Updater(token = TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('set_username',set_username,pass_args=True))
    dp.add_handler(CommandHandler('set_password',set_password,pass_args=True))
    dp.add_handler(CommandHandler('save_schedule',save_schedule))
    dp.add_handler(CommandHandler('get_schedule',get_schedule,pass_args=True))
    dp.add_handler(CommandHandler('next',callback_get_time))
    
    updater.start_polling()




def callback_get_time(bot,update):
 
    date = update.message.date
    time = datetime.time(date.hour,date.minute,date.second)
    weekday = date.isoweekday()
    
    days = 0
    
    if(weekday == 7):
        
        days = 1
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


if __name__ == '__main__':
    main()