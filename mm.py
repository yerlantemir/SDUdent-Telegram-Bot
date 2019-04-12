from database import Database
db = Database()

browsers = db.get(['users']).val()
print(browsers['260477200'].keys())

# for user in browsers:
    
#     try:
#         chat_id = user[0]
#         username = user[-1]['username']
#         password = user[-1]['password']
    
#     except:
#         continue
    
#     l.append((chat_id,username,password))    
# print(l)
# # users = []
# for i in range(5):
    
#     user = {}
#     user['chat_id'] = i
#     user['sc'] = 'scc'
#     users.append(user)

# l2 = [k['chat_id'] for k in users]
# print(l2)
