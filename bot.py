import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler,MessageHandler,Filters,ConversationHandler
import datetime
from scrapper import Schedule
import time
from Facade import BotFacade
from selenium.common.exceptions import NoSuchElementException
from database import Database
import ast


db = Database()


def start(bot,update):
    chat_id = get_chat_id(update)
    global db
    db.set_data(["users",chat_id],chat_id)
    send_message(bot,chat_id,'Welcome to our bot!')


def set_username(bot,update,args):
    global db
    chat_id = get_chat_id(update)
    
    try:
    
        username = args[0]
    
    except IndexError:

        send_message(bot,chat_id,'Your foggot to enter your login(example: /set_username 170103024),please,try again')
        return
    db.set_data(["users",chat_id,"username"],username)
    send_message(bot,chat_id,'Username saved')


def set_password(bot,update,args):

    chat_id = get_chat_id(update)
    
    try:
        
        password = args[0]

    except IndexError:

        send_message(bot,chat_id,'Your foggot to enter your password(example: /set_password 170103024),please,try again')
        return

    db.set_data(["users",chat_id,"password"],password)
    send_message(bot,chat_id,'Password saved')
    

def save_schedule(bot,update,job_queue):
    global db
    
    chat_id = get_chat_id(update)
    username = db.get(["users",chat_id,"username"]).val()
    password = db.get(["users",chat_id,"password"]).val()
    
    if(username == '' or password == ''):
        send_message(bot,chat_id,'You did not entered your login or password,please,firtsly use /set_username and /set_password methods')
        return

    send_message(bot,chat_id,'We are getting data from portal,wait about 10 seconds')
    
    try:

        sc = Schedule(username,password)

    except NoSuchElementException:

        send_message(bot,chat_id,'Your entered incorrect username/password,so we could not get your schedule,try again!')
        return
    
    schedule_data = sc.get_schedule_data()
    grades_data = sc.get_grades_data()
    db.set_data(["users",chat_id,"schedule_data"],schedule_data)
    db.set_data(["users",chat_id,"grades_data"],grades_data)
    send_message(bot,chat_id,'We got your schedule,you are welcome to use!')
    job_queue.run_repeating(notify_grades,15,context=(sc,chat_id))


def notify_grades(bot,job):
    
    global db
    sc = job.context[0]
    chat_id = job.context[1]
    old_grades = db.get(["users",chat_id,"grades_data"]).val()

    new_grades = sc.get_grades_data() 
    updates = get_update_in_grades(old_grades,new_grades)

    if len(updates) != 0:
        for i in range(len(updates)):
            index_of_changed_subject_grade = updates[i]
            subject = new_grades[index_of_changed_subject_grade]['name']
            new_grade = new_grades[index_of_changed_subject_grade]['grade']
            bot.send_message(chat_id = chat_id,text = 'Поменялась ваша оценка по предмету {} на {}'.format(subject,new_grade))

    db.set_data(["users",chat_id,"grades_data"],new_grades)

def get_schedule(bot,update,args):

    chat_id = get_chat_id(update)
    
    try:
        
        day = int(args[0])

    except IndexError:
        send_message(bot,chat_id,'Your foggot to enter day(example: /get_schedule 2 ,to get tuesday\'s schedule),please,try again')
        return
    global db
    weekdays = db.get(["users",chat_id,"schedule_data"]).val()
    
    for i in range(len(weekdays[day])):
        send_message(bot,chat_id,'{}){}'.format(i+1,weekdays[day][i]))





def main():

    facade = BotFacade()
    updater = facade.getBot()
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('set_username',set_username,pass_args=True))
    dp.add_handler(CommandHandler('set_password',set_password,pass_args=True))
    dp.add_handler(CommandHandler('save_schedule',save_schedule,pass_job_queue=True))
    dp.add_handler(CommandHandler('get_schedule',get_schedule,pass_args=True))
    dp.add_handler(CommandHandler('next',callback_get_time))
    
    updater.start_polling()









def send_message(bot,chat_id,send_text):
    try:
        bot.send_message(chat_id = chat_id,text = send_text,parse_mode = 'HTML')
    except:
        print('No such chat id')




def get_chat_id(update):
    return update.message.chat_id


def get_update_in_grades(old_grades,new_grades):
    
    updates = []
    
    for i in range(len(old_grades) or len(new_grades)):
        
        old_grade = old_grades[i]['grade']
        new_grade = new_grades[i]['grade']
      
        
        if(old_grade != new_grade):
            updates.append(i)

    return updates





def callback_get_time(bot,update):
    global db
    chat_id = get_chat_id(update)
    
    weekdays = db.get(["users",chat_id,"schedule_data"]).val()
    date = update.message.date
    time = datetime.time(date.hour,date.minute,date.second)
    weekday = date.isoweekday()
    
    days = 0
    
    if(weekday == 7):
        days = 1
        weekday = 1

    indexOfMin = closest_index(time,weekday,weekdays)
    
    if days > 0:

        indexOfMin = 0

    next_lesson = ast.literal_eval(weekdays[weekday][indexOfMin])
    next_lesson_time = datetime.time(next_lesson['time']['hour'],next_lesson['time']['minute'],00)
    
    next_lesson_date = datetime.datetime(date.year,
    date.month,date.day+days,next_lesson_time.hour,next_lesson_time.minute,00)

    bot.send_message(chat_id = update.message.chat_id , 
            text = 'Your next lesson is {}\nWhere?{}\nTeacher:{} \nuntil lesson:{}'.format(next_lesson['title']
                ,next_lesson['room'],
                next_lesson["teacher_name"],next_lesson_date - date))

    
    




def closest_index(time,weekday,weekdays):

    my_time_minutes = time.hour*60 + time.minute
    min = 24*60
    indexOfMin = 0

    for i in range(len(weekdays[weekday])):
        subjects = ast.literal_eval(weekdays[weekday][i])
        subject_time = subjects['time']
        minutes = subject_time['hour']*60+subject_time['minute']
        difference = minutes - my_time_minutes 

        if(difference < min and difference > 0):

            min = difference
            indexOfMin = i
        

    return indexOfMin




if __name__ == '__main__':
    main()