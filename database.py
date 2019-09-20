from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGO_URI)

db = client['heroku_rplqc9l0']
collection_grades = db['sdudents-database']
collection_feedback = db['feedback']
collection_features = db['features']


def update_grades(chat_id, new_grades):
    # difference ex : ('average' :'85')
    # difference[0] => 'average'

    collection_grades.update_one({
        'chat_id': chat_id
    }, {'$set':
        {
            'semester_data': new_grades
        }
    }, True)


def insert_user(user_grades, user_info):
    chat_id = user_grades['chat_id']
    username = user_grades['username']
    password = user_grades['password']
    semester_data = user_grades['semester_data']
    collection_grades.update_one({'chat_id': chat_id}, {'$set': {'username': username,
                                                                 'password': password,
                                                                 'semester_data': semester_data,
                                                                 }}, True)
    collection_features.update_one({'chat_id': chat_id}, {'$set': {
        'name_surname': user_info['name_surname'],
        'feature': user_info['feature'],
        'program': user_info['program']
    }})


def find_by_chat_id(chat_id):
    return collection_features.find_one({'chat_id': chat_id})


def change_state(chat_id, info_allow_state):
    collection_features.update_one({
        'chat_id': chat_id
    }, {'$set':
        {
            'info_allow_state': info_allow_state
        }

    }, True)


def add_feedback(chat_id, message_text):
    collection_feedback.insert_one({'chat_id': chat_id,
                                    'message': message_text})
