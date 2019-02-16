import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler,MessageHandler,Filters,ConversationHandler
import datetime
import secret_data as sd

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

username = ''
password = ''

USERNAME,PASSWORD,GENDER = range(3)
weekdays = {1:[datetime.time(15,00,0) ],
            
            2:[datetime.time(10,00,0),    
            datetime.time(11,00,0),   
            datetime.time(12,00,0),    
            datetime.time(13,00,0),   
            datetime.time(14,0,0), 
            datetime.time(16,0,0) ],
            
            3:[datetime.time(9,00,0),    
            datetime.time(10,00,0),   
            datetime.time(12,00,0),    
            datetime.time(13,00,0),   
            datetime.time(14,00,0) ],
            
            4:[datetime.time(10,00,0),    
            datetime.time(11,00,0),   
            datetime.time(12,00,0),    
            datetime.time(14,00,0),   
            datetime.time(20,00,0) ],
            
            5:[datetime.time(13,00,0),    
            datetime.time(14,00,0),   
            datetime.time(19,00,0) ]}



def callback_get_time(bot,update):
 
    date = update.message.date
    time = datetime.time(date.hour,date.minute,date.second)
    weekday = date.isoweekday()
    days = 0

    if(weekday > 5):
        days += 8 - weekday
        weekday = 1
    
    indexOfMin = closest_index(time,weekday)
    if days > 0:
        indexOfMin = 0
    next_lesson_time = weekdays[weekday][indexOfMin]
    
    next_lesson_date = datetime.datetime(date.year,
    date.month,date.day+days,next_lesson_time.hour,next_lesson_time.minute,00)

    bot.send_message(chat_id = update.message.chat_id , 
            text = 'Until next lesson:{}'.format(next_lesson_date - date))

    
    
def closest_index(time,weekday):
    my_time_minutes = time.hour*60 + time.minute
    min = 24*60
    indexOfMin = 0

    global weekdays
    for i in range(len(weekdays[weekday])):
        
        minutes = weekdays[weekday][i].hour*60+weekdays[weekday][i].minute
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