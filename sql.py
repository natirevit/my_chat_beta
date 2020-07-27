import sqlite3, config, re, config
from datetime import datetime as dt



#region sql

class sql:

    #region init

    def __init__(self, dbName):
        self.db = self.connectDb(dbName)

    def connectDb(self, dbName):
        return sqlite3.connect(dbName)
    
    def close(self):
        self.db.close()

    #endregion


    #region login sql

    def login(self,name):   
        self.db.execute("update users set logged_in = 1, last_transaction=? where user_name=?", (dt.now().strftime(config.DATE_FORMAT), name))
        self.db.commit()
        return self.db.execute("select paswd from users where user_name=?", (name,)).fetchone()[0]


    def check_user_exist(self,name): 
        return self.db.execute("select id from users where user_name=?", [name]).fetchone()

    def get_user_id(self,name): 
        return self.db.execute("select id from users where user_name=?", (name,)).fetchone()[0]     

    def get_user_name(self,id):
        return self.db.execute("select user_name from users where id=?", (str(id),)).fetchone()[0] 

    #endregion


    #region sendMsg sql

    def insert_massage(self,msg): 
        self.db.execute("""insert into messages (sender ,receiver, creation_date, sbjct, msg, visited)
        VALUES (?,?,?,?,?,0)""",(msg.sender, 
                                                     msg.receiver,
                                                     msg.creation_date,
                                                     msg.sbjct,
                                                     msg.msg))
        self.db.commit()

    # There is no need to lock the db - becouse its the same transaction:
    def get_sent_msg_id(self):
        return self.db.execute("select max(id) from messages").fetchone()

    #endregion


    #region getMsgs sql

    def get_all_msgs(self, receiver, sender, visited): 
        visited = bool(visited)
        return self.db.execute("""select id, sender ,receiver, creation_date, sbjct, msg 
                               from messages where receiver = ? and sender = ? 
                               """ +  (" and visited = 0" if (not visited) else "" ) , (receiver, sender)).fetchall()

    def set_visited_all(self,receiver, sender):
        self.db.execute("update messages set visited = 1 where receiver = ? and sender = ?",
                   (receiver,sender))
        self.db.commit()

    def get_msg_by_id(self, id):
        return self.db.execute("select * from messages where id = ?", (str(id),)).fetchone()

    def set_visited_one(self,id):
        self.db.execute("update messages set visited = 1 where id = ?", (str(id),))
        self.db.commit()

    #endregion    


    #region delete

    def delete_message_by_id(self,id):
        self.db.execute("delete from messages where id = ?", (str(id),)) 
        self.db.commit()

    #endregion

#endregion

#region injection

class validate:
    def __init__(self):
        self.regStr = r"\A[A-Za-z]*\Z"
        self.regInt = r"\A[0-9]*\Z"
        self.regStrInt = r"\A[A-Za-z0-9*]\Z"
        self.regFullTxt = r"\A[ -&(-~]*\Z"

    def isStrInput(self, x):
        patern = re.compile(self.regStr)
        if patern.match(x):
            return True

    def isIntInput(self, x):
        patern = re.compile(self.regInt)
        if patern.match(str(x)):
            return True

    def isFullTxtInput(self, x):
        patern = re.compile(self.regFullTxt)
        if patern.match(x):
            return True

    def isStrIntInput(self, x):
        patern = re.compile(self.regFullTxt)
        if patern.match(x):
            return True

#endregion