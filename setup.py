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



db = Database()


def start(bot,update):
    
    chat_id = get_chat_id(update)
    global db
    send_message(bot,chat_id,"Hi SDUdent!!"\
                            "\n" \
                            "\n" \
                            "Tell me your username and password from portal and I will notify you about new grades!"\
                            "\n" \
                            "\n" \
                            "Type /help to show list of avaible commands" \
                            "\n" \
                            "\n" \
                            "Good luck!")


def set_student_number(bot,update,args):
    global db
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

    chat_id = get_chat_id(update)
    
    try:
        
        password = args[0]

    except IndexError:

        send_message(bot,chat_id,'You have not entered you password(example: /set_p 170103024),please,try again')
        return

    password = crpt.encrypt(password)
    db.set_data(["users",chat_id,"password"],password)
    send_message(bot,chat_id,'Password saved')
    

def notify_on(bot,update,job_queue):
    
    global db
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

        sc = Schedule(username,password)
        db.set_data(["users",chat_id,"entered"],True)
    except NoSuchElementException:

        send_message(bot,chat_id,'You entered incorrect username/password,so we could not get your schedule,try again!')
        return
    
    grades_data = sc.get_grades_data()
    db.set_data(["users",chat_id,"grades_data"],grades_data)
    send_message(bot,chat_id,'Yahooo! I did it! From now I will notify you about updated grades and absences!!')
    job_queue.run_repeating(notify_grades,600,context=(sc,chat_id))


def notify_grades(bot,job):
    
    global db
    sc = job.context[0]
    chat_id = job.context[1]
    old_grades = db.get(["users",chat_id,"grades_data"]).val()

    new_grades = sc.get_grades_data() 
    updates,appends = get_update_in_grades(old_grades,new_grades)
    grade_states = ['1st midterm','2nd midterm','final','average']
    
    if appends != 0:
        print(updates,'updates:')
        for i in range(len(updates)):

            if len(updates[i]) != 0:

                for k in range(len(updates[i])):

                    subject_name = old_grades[updates[i][k]]['name']
                    
                    if i == 0:

                        new = new_grades[updates[i][k]]['att']
                        print(new)
                        old = old_grades[updates[i][k]]['att']
                        print(old)
                        if old == '0':
                            send_message(bot,chat_id,'Absence count by subject \"{}\" was changed to {}'.format(subject_name,new))
                        
                        else:
                            send_message(bot,chat_id,'Absence count by subject \"{}\" was changed from {} to {}'.format
                                (subject_name,old,new))
                    else:
                        
                        new = new_grades[updates[i][k]]['grade'][grade_states[i-1]]
                        old = old_grades[updates[i][k]]['grade'][grade_states[i-1]]
                        print(new,old)
                        if old == '':
                            send_message(bot,chat_id,'{} grade by subject \"{}\" : {}'.format(grade_states[i-1],subject_name,new))
                        
                        else:
                            send_message(bot,chat_id,'{} grade by subject \"{}\" was changed from {} to {}'.
                                format(grade_states[i-1],subject_name,old,new))


                
  

    db.set_data(["users",chat_id,"grades_data"],new_grades)

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

    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('set_sn',set_student_number,pass_args=True))
    dp.add_handler(CommandHandler('set_p',set_password,pass_args=True))
    dp.add_handler(CommandHandler('on',notify_on,pass_job_queue=True))
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



