import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler,MessageHandler,Filters,ConversationHandler
import datetime
import secret_data as sd
import scrapper
import time
from pprint import pprint
from selenium.common.exceptions import NoSuchElementException

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

user = {}


weekdays = {}

grades = {}






def start(bot,update):

    chat_id = get_chat_id(update)
    global user 
    user = {chat_id:scrapper.Schedule()}
    send_message(bot,chat_id,'Welcome to our bot!')


def set_username(bot,update,args):

    global user
    chat_id = get_chat_id(update)
    
    try:
    
        username = args[0]
    
    except IndexError:

        send_message(bot,chat_id,'Your foggot to enter your login(example: /set_username 170103024),please,try again')
        return
    
    user[chat_id].set_username(username)
    send_message(bot,chat_id,'Username saved')


def set_password(bot,update,args):
    

    global user
    chat_id = get_chat_id(update)
    
    try:
        
        password = args[0]

    except IndexError:

        send_message(bot,chat_id,'Your foggot to enter your password(example: /set_password 170103024),please,try again')
        return
    
    user[chat_id].set_password(password)
    send_message(bot,chat_id,'Password saved')
    

def save_schedule(bot,update):
    
    global user,weekdays
    
    chat_id = get_chat_id(update)
    username = user[chat_id].username
    password = user[chat_id].password
    
    if(username == '' or password == ''):
        send_message(bot,chat_id,'You did not entered your login or password,please,firtsly use /set_username and /set_password methods')
        return

    send_message(bot,chat_id,'We are getting data from portal,wait about 10 seconds')
    
    try:
        user[chat_id].login()
    
    except NoSuchElementException:
        send_message(bot,chat_id,'Your entered incorrect username/password,so we could not get your schedule,try again!')
        return
    
    weekdays[chat_id] = user[chat_id].get_schedule_data()
    send_message(bot,chat_id,'We got your schedule,you are welcome to use!')






def get_schedule(bot,update,args):

    chat_id = get_chat_id(update)
    
    try:
        
        day = int(args[0])

    except IndexError:
        send_message(bot,chat_id,'Your foggot to enter day(example: /get_schedule 2 ,to get tuesday\'s schedule),please,try again')
        return
    
    global weekdays
    
    for i in range(len(weekdays[chat_id][day])):
        send_message(bot,chat_id,'{}){}'.format(i+1,weekdays[chat_id][day][i]))



def notify_grades_on(bot,update,job_queue):
    
    chat_id = get_chat_id(update)
    
    global grades
    grades[chat_id] = user[chat_id].get_grades_data()
    job_queue.run_repeating(notify_grades,20,context=chat_id)





def notify_grades(bot,job):
    

    chat_id = job.context
    global grades
    old_grades = grades[chat_id]

    new_grades = {}
    new_grades[chat_id] = user[chat_id].get_grades_data()
    updates = get_update_in_grades(old_grades,new_grades[chat_id])
    
    if len(updates) != 0:
        for i in range(len(updates)):
            subject = new_grades[chat_id][i]['name']
            new_grade = new_grades[chat_id][i]['grade']
            bot.send_message(chat_id = chat_id,text = 'Поменялась ваша оценка по предмету {} на {}'.format(subject,new_grade))

    grades = new_grades





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
    dp.add_handler(CommandHandler('gr_on',notify_grades_on,pass_job_queue=True))
    
    updater.start_polling()








def send_message(bot,chat_id,send_text):
    try:
        bot.send_message(chat_id = chat_id,text = send_text,parse_mode = 'HTML')
    except:
        print('No such chat id')


def get_chat_id(update):
    return update.message.chat_id


def get_user_data(chat_id):
    username = user[chat_id]['username']
    password = user[chat_id]['password']
    return username,password


def get_update_in_grades(old_grades,new_grades):
    
    updates = []
    
    for i in range(len(old_grades) or len(new_grades)):
        
        old_grade = old_grades[i]['grade']
        new_grade = new_grades[i]['grade']
      
        
        if(old_grade != new_grade):
            updates.append(i)

    return updates


def callback_get_time(bot,update):
    chat_id = get_chat_id(update)
    date = update.message.date
    time = datetime.time(date.hour,date.minute,date.second)
    weekday = date.isoweekday()
    
    days = 0
    
    if(weekday == 7):
        days = 1
        weekday = 1

    indexOfMin = closest_index(time,weekday,chat_id)
    
    if days > 0:

        indexOfMin = 0

    next_lesson = weekdays[chat_id][weekday][indexOfMin]
    next_lesson_time = next_lesson.time
    
    next_lesson_date = datetime.datetime(date.year,
    date.month,date.day+days,next_lesson_time.hour,next_lesson_time.minute,00)

    bot.send_message(chat_id = update.message.chat_id , 
            text = 'Your next lesson is {}\nWhere?{}\nTeacher:{} \nuntil lesson:{}'.format(next_lesson.title,next_lesson.room,
                next_lesson.teacher_name,next_lesson_date - date))

    
    

def closest_index(time,weekday,chat_id):

    my_time_minutes = time.hour*60 + time.minute
    min = 24*60
    indexOfMin = 0

    global weekdays
    for i in range(len(weekdays[chat_id][weekday])):
        
        subject_time = weekdays[chat_id][weekday][i].time
        minutes = subject_time.hour*60+subject_time.minute
        difference = minutes - my_time_minutes 

        if(difference < min and difference > 0):

            min = difference
            indexOfMin = i
        

    return indexOfMin


if __name__ == '__main__':
    main()