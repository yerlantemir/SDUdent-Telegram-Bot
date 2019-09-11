start_message = "Hi SDUdent!!" \
                "\n" \
                "\n" \
                "If you called this command accidentally call /cancel" \
                "\n" \
                "\n" \
                "To notify you about new grades,I need your student number and password from out portal" \
                "\n" \
                "\n" \
                "Enter your login below:"

password_message = 'Now,enter your password:'
wait_message = 'I am getting your grades data from portal,wait about 10 seconds'

incorrect_data_message = 'You entered incorrect username/password,so I could not get your schedule,try again!' \
                         "\n" \
                         "\n" \
                         "Enter your login below:"

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


def found_message(name_surname, program, probability):
    return f'this is {name_surname} from {program} , sim = {probability}'
