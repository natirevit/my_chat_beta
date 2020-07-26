import sqlite3, config

def connectDb():
    return sqlite3.connect(config.DB_NAME)

test_str = "select * from users"

def login(name): 
    return "select paswd from users where user_name = '" + name + "'"

def check_user_exist(name): 
    return "select id from users where user_name = '" + name + "'"

def insert_massage(msg): 
    return """insert into messages (sender ,receiver, creation_date, sbjct, msg, visited)
           VALUES (""" + "'{0}','{1}','{2}','{3}','{4}',0".format(msg.sender, 
                                                      msg.receiver,
                                                      msg.creation_date,
                                                      msg.sbjct,
                                                      msg.msg) + ")"

def get_sent_msg_id():
    return "select max(id) from messages"

def get_user_id(name): 
    return "select id from users where user_name = '" + name + "'"     

def get_user_name(id):
    return "select user_name from users where id = " + str(id) 

def get_all_msgs(receiver, sender, visited): 
    command = "select id, sender ,receiver, creation_date, sbjct, msg from messages where receiver = '" + receiver +  "' and sender = '" + sender + "'"
    if (not visited):
        command += " and visited = 0" 

    return command                                                   
            
def set_visited_all(receiver, sender):
    return "update messages set visited = 1 where receiver = '" + receiver + "' and sender = '" + sender + "'"

def set_visited_one(id):
    return "update messages set visited = 1 where id = " + str(id)

def get_msg_by_id(id):
    return "select * from messages where id = " + str(id)

def delete_message_by_id(id):
    return "delete from messages where id = " + str(id) 
