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
import AESencoder as crpt
import os
import threading

def start(bot,update):
    
    chat_id = get_chat_id(update)
    send_message(bot,chat_id,"Hi SDUdent!!"\
                            "\n" \
                            "\n" \
                            "Follow giving instructions to get notifications about your grades and absences, which will change in portal."\
                            "\n" \
                            "\n" \
                            "1)/set_sn your_student_number (ex: /set_sn 170103024)"\
                            "\n" \
                            "2)/set_p you_password (ex: /set_p kyzylorda1999)"
                            "\n" \
                            "3)/on (activate process)"
                            "\n" \
                            "\n" \
                            "Type /help to show list of avaible commands" \
                            "\n" \
                            "\n" \
                            "Good luck!")


def set_student_number(bot,update,args):

    db = Database()
    chat_id = get_chat_id(update)
    
    try:
    
        username = args[0]
    
    except IndexError:

        send_message(bot,chat_id,'You have not entered(example: /set_sn 170103024),please,try again')
        return

    username = crpt.encrypt(username)
    db.set_data(["users",chat_id,"username"],username)
    send_message(bot,chat_id,'Username saved')


def set_password(bot,update,args):
    db = Database()
    chat_id = get_chat_id(update)
    
    try:
        
        password = args[0]

    except IndexError:

        send_message(bot,chat_id,'You have not entered you password(example: /set_p 170103024),please,try again')
        return

    password = crpt.encrypt(password)
    db.set_data(["users",chat_id,"password"],password)
    send_message(bot,chat_id,'Password saved')
    


def notify_on(bot,update):
    
    db = Database()
    chat_id = get_chat_id(update)

    entered = db.get(["users",chat_id,"entered"]).val()
    
    if(bool(entered)):
        send_message(bot,chat_id,"I have already got your data,no need to call this command anymore")
        return

    username = crpt.decrypt(db.get(["users",chat_id,"username"]).val())
    password = crpt.decrypt(db.get(["users",chat_id,"password"]).val())

    if(username == '' or password == ''):
        send_message(bot,chat_id,'You have not entered your login or password,please,firtsly use /set_sn and /set_p commands')
        return

    send_message(bot,chat_id,'I am getting your grades data from portal,wait about 10 seconds')
    
    try:

        sc = Schedule()
        sc.login(username,password)
        db.set_data(["users",chat_id,"entered"],True)

    except NoSuchElementException:

        db.set_data(["users",chat_id,"entered"],False)
        send_message(bot,chat_id,'You entered incorrect username/password,so we could not get your schedule,try again!')
        return
    
    grades_data = sc.get_grades_data()
    sc.close_browser()
    db.set_data(["users",chat_id,"grades_data"],grades_data)
    send_message(bot,chat_id,'Yahooo! I did it! From now I will notify you about updated grades and absences!!')


def notify_grades(bot_):
    

    while(True):

        sc = Schedule()
        print('I AM WORKING !!!')
        db = Database()
        users = db.get(['users'])
        
        for user in list(users.val().items()):
            
            if 'entered' not in user[-1].keys():
                continue

            st_id = crpt.decrypt(user[-1]['username'])
            password = crpt.decrypt(user[-1]['password'])
            chat_id = user[0]
            
            try:
            
                sc.clear()
                sc.login(st_id,password)
            
            except NoSuchElementException:
                continue
            
            if 'grades_data' not in user[-1].keys():
                continue
                
            old_grades = user[-1]['grades_data']
            
            new_grades = sc.get_grades_data()

            try:
                sc.quit()
            except NoSuchElementException:
                continue
            updates,appends = get_update_in_grades(old_grades,new_grades)
            notify_about_new_grade(bot_,appends,updates,new_grades,old_grades,chat_id)

            db.set_data(["users",chat_id,"grades_data"],new_grades)
        sc.close_browser()
        time.sleep(600)


def notify_about_new_grade(bot_,appends,updates,new_grades,old_grades,chat_id):
    
    grade_states = ['1st midterm','2nd midterm','final','average']

    if appends != 0:
        for i in range(len(updates)):

            if len(updates[i]) != 0:

                for k in range(len(updates[i])):

                    subject_name = old_grades[updates[i][k]]['name']
                    
                    if i == 0:

                        new = new_grades[updates[i][k]]['att']
                        old = old_grades[updates[i][k]]['att']
                        if old == '0':
                            send_message(bot_,chat_id,'Absence count by subject \"{}\" was changed to {}'.format(subject_name,new))
                        
                        else:
                            send_message(bot_,chat_id,'Absence count by subject \"{}\" was changed from {} to {}'.format
                                (subject_name,old,new))
                    else:
                        
                        new = new_grades[updates[i][k]]['grade'][grade_states[i-1]]
                        old = old_grades[updates[i][k]]['grade'][grade_states[i-1]]
                        print(new,old)
                        if old == '':
                            send_message(bot_,chat_id,'{} grade by subject \"{}\" : {}'.format(grade_states[i-1],subject_name,new))
                        
                        else:
                            send_message(bot_,chat_id,'{} grade by subject \"{}\" was changed from {} to {}'.
                                format(grade_states[i-1],subject_name,old,new))


                
  


# def get_schedule(bot,update,args):

#     chat_id = get_chat_id(update)
    
#     try:
        
#         day = int(args[0])

#     except IndexError:
#         send_message(bot,chat_id,'Your foggot to enter day(example: /get_schedule 2 ,to get tuesday\'s schedule),please,try again')
#         return
#     global db
#     weekdays = db.get(["users",chat_id,"schedule_data"]).val()
    
#     for i in range(len(weekdays[day])):
#         send_message(bot,chat_id,'{}){}'.format(i+1,weekdays[day][i]))


def unknown_command(bot, update):
    send_message(bot,update.message.chat_id,'Unrecognized command. Say what?')


def help(bot, update):
    chat_id = get_chat_id(update)
    send_message(bot,chat_id,"Avaible commands:"\
                                "\n" \
                                "\n" \
                                "1. /set_sn - update student number" \
                                "\n" \
                                "2. /set_p - update password" \
                                "\n" \
                                "3. /on - start notifying " \
                                "\n" \
                                "4. /help - list of commands")





def main():
    
    
    facade = BotFacade()
    updater = facade.getBot()
    dp = updater.dispatcher

    thread = threading.Thread(target=notify_grades,args=(updater.bot,))
    thread.start()

    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('set_sn',set_student_number,pass_args=True))
    dp.add_handler(CommandHandler('set_p',set_password,pass_args=True))
    dp.add_handler(CommandHandler('on',notify_on))
    dp.add_handler(CommandHandler('help', help))    
    dp.add_handler(MessageHandler(Filters.command, unknown_command))
    updater.start_polling()







def send_message(bot,chat_id,send_text):
    try:
        bot.send_message(chat_id = chat_id,text = send_text,parse_mode = 'HTML')
    except:
        print('No such chat id')




def get_chat_id(update):
    return update.message.chat_id


def get_update_in_grades(old_grades,new_grades):
    
    appends = 0
    updates = [[],[],[],[],[]]
    grade_states = ['1st midterm','2nd midterm','final','average']       
    for i in range(len(old_grades) or len(new_grades)):
        
        for k in range(0,4):
            if old_grades[i]['grade'][grade_states[k]] != new_grades[i]['grade'][grade_states[k]]:
                updates[k+1].append(i)
                appends += 1
        old_att = old_grades[i]['att']
        new_att = new_grades[i]['att']

        
        if(old_att != new_att):
            updates[0].append(i)
            appends += 1
    return updates,appends


    
if __name__ == '__main__':
    main()




# def callback_get_time(bot,update):
#     global dbsend_message
#     chat_id = get_chat_id(update)
    
#     weekdays = db.get(["users",chat_id,"schedule_data"]).val()
#     date = update.message.date
#     time = datetime.time(date.hour,date.minute,date.second)
#     weekday = date.isoweekday()
    
#     days = 0
    
#     if(weekday == 7):
#         days = 1
#         weekday = 1

#     indexOfMin = closest_index(time,weekday,weekdays)
    
#     if days > 0:

#         indexOfMin = 0

#     next_lesson = ast.literal_eval(weekdays[weekday][indexOfMin])
#     next_lesson_time = datetime.time(next_lesson['time']['hour'],next_lesson['time']['minute'],00)
    
#     next_lesson_date = datetime.datetime(date.year,
#     date.month,date.day+days,next_lesson_time.hour,next_lesson_time.minute,00)

#     bot.send_message(chat_id = update.message.chat_id , 
#             text = 'Your next lesson is {}\nWhere?{}\nTeacher:{} \nuntil lesson:{}'.format(next_lesson['title']
#                 ,next_lesson['room'],
#                 next_lesson["teacher_name"],next_lesson_date - date))

    
    




# def closest_index(time,weekday,weekdays):

#     my_time_minutes = time.hour*60 + time.minute
#     min = 24*60
#     indexOfMin = 0

#     for i in range(len(weekdays[weekday])):
#         subjects = ast.literal_eval(weekdays[weekday][i])
#         subject_time = subjects['time']
#         minutes = subject_time['hour']*60+subject_time['minute']
#         difference = minutes - my_time_minutes 

#         if(difference < min and difference > 0):

#             min = difference
#             indexOfMin = i
        

#     return indexOfMin



