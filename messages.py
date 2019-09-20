start_message = "Hi SDUdent!!" \
                "\n" \
                "\n" \
                "If you called this command accidentally call /cancel" \
                "\n" \
                "\n" \
                "To notify you about new grades,I need your student number and password from out portal" \
                "\n" \
                "\n" \
                "Enter your student number below:"

password_message = 'Now,enter your password:'
wait_message = 'I am getting your grades data from portal,wait about 10 seconds'

incorrect_data_message = 'You entered incorrect username/password,so I could not get your schedule,try again!' \
                         "\n" \
                         "\n" \
                         "Enter your student number below:"

done_message = 'Yahooo! I did it! From now I will notify you about updated grades and absences!!' \
               "\n" \
               "\n" \
               'There is a "people finding functional" on this but,do you want to be found by photo?'

help_message = "Avaible commands:" \
               "\n" \
               "\n" \
               "1. /set_sn - update student number" \
               "\n" \
               "2. /set_p - update password" \
               "\n" \
               "3. /on - start notifying " \
               "\n" \
               "4. /help - list of commands"

what_message = 'Unrecognized command. Say what?'

more_than_one_message = 'More than one face detected,please crop face of person you want to find,and send again!'

no_face_message = 'There is no face in this picture!'

not_subscribed_message = 'This person not subscribed to this bot!'

disabled_info_message = 'This person disabled his information!'

feedback_start_message = 'Write your feedback below:'

send_photo_message = 'This is sdudent finder function,you can find sdudent\'s name and program by his picture!' \
                     'However if you don\'t want to be found by another user,just call /change_state and I will update'\
                     'your status of privacy' \
                     '\n' \
                     '\n' \
                     'Send me photo of person you want to find:'

thanks_message = 'Thanks for your feedback!'

wait_searching_message = 'Wait about 10 seconds,I am searching for him!'

to_all_users_message = 'Hello sdudent! I am back and glad to tell you that there are some updates!' \
                       '\n' \
                       '\n' \
                       '1.There is a new option which can help you find someone from sdu by his/her picture' \
                       'Call /find_user command and test it out!' \
                       '\n' \
                       '\n' \
                       '2.If you have any wishes or found an error,' \
                       'please write me about it by calling /feedback command.' \
                       '\n' \
                       '\n' \
                       '3.Bot became more user-friendly,so share info about me with friends!'


def found_message(name_surname, program, probability):
    return f'this is <{name_surname}> from <{program}> , probability: {round(probability.item() * 100)}%'
