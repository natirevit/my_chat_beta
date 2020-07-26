from flask import Flask, request, session, g
import os, sqlite3, datetime
from datetime import datetime as dt 
import config, sql, json


app = Flask(__name__)
app.secret_key = config.SKEY



#region authorization and pre || after request


@app.before_request
def before_request():
    if ((not request.endpoint == "login") and (not request.endpoint == "clearDB")):        
        if (not "user" in session):
            return "sprinklers on, you'r not logged in", 401

    g.db = sql.connectDb()


@app.after_request
def after_request(response):
    if(hasattr(g, "db")):
        g.db.close()

    return response


@app.route('/login', methods=["GET","POST"])
def login():

    user = request.form['user'] 
    paswd = request.form['paswd']

    if (not checkUserExist(user)):
        return "user " + user  + " unexist in the system", 404
    
    #simple sql injection check
    if (not ' ' in user):
        dbPasswd = g.db.execute(sql.login(user)).fetchone()[0]
        if dbPasswd == paswd: 
            session['user'] = user
            return "you are in " + user, 200 
        else:
            return "passward or user not correct", 401

    return "user musnt have space", 401


@app.route('/logout', methods=["GET","POST"])
def logout():

    if 'user' in session:
        session.pop('user')

    return "see you soon"
    

#endregion



#region web


@app.route('/sendMsg/<string:toUsr>', methods=['POST'])
def sendMsg(toUsr):

    if (not checkUserExist(toUsr)):
        return "user " + toUsr  + " unexist in the system", 404
    elif (toUsr == session["user"]):
        return "dont talk to yourself", 404

    msg = message((session['user'], toUsr,
                   dt.now().strftime(config.DATE_FORMAT),
                   request.form['subject'], request.form['content']))

    g.db.execute(sql.insert_massage(msg))
    g.db.commit()

    msgId = g.db.execute(sql.get_sent_msg_id()).fetchone()[0]

    return "sent successfuly - msg number is " + str(msgId), 200


@app.route('/getMultyMsg/<string:fromUsr>/<int:visited>',methods=['GET','POST'])
def getMultyMsg(fromUsr,visited):

    if (not checkUserExist(fromUsr)):
        return "user " + fromUsr  + " unexist in the system", 404
    elif (fromUsr == session["user"]):
        return "write name of someone else", 404

    Sender = fromUsr
    Me = session['user']

    msgs = g.db.execute(sql.get_all_msgs(Me, fromUsr, visited)).fetchall()

    if (not msgs):
        return "there are no " + ( "" if visited else "new ") + "messages", 204

    mailPack = {}
    for msg in msgs: 
        oMsg = message(msg[1:])
        mailPack['msgId ' + str(msg[0]) + ' content'] = oMsg.toDict()

    g.db.execute(sql.set_visited_all(Me, Sender))
    g.db.commit()
    
    return mailPack 


@app.route('/getOneMsg/<string:sign>', methods=['GET','POST'])
def getOneMsg(sign):

    msg = None

    if (sign.isnumeric()):

        msg = g.db.execute(sql.get_msg_by_id(sign)).fetchone()
        if (not msg ):
            return "no msg with this id"

        oMsg = message(msg[1:]) 
        if (oMsg.sender != session["user"] and oMsg.receiver != session["user"]):
            return "this isnt your message", 401

    else:

        if (not checkUserExist(sign)):
            return "user " + sign  + " unexist in the system", 404
        elif (sign == session["user"]):
            return "write a name of someone else", 404
        
        msgs = g.db.execute(sql.get_all_msgs(session["user"],sign,True)).fetchall()

        if ( not msgs ):
            return "no msg from " + sign, 204

        # returm the last message sent by the user
        msg = max(msgs,key=lambda m: dt.strptime(message(m[1:]).creation_date,config.DATE_FORMAT))

    g.db.execute(sql.set_visited_one(msg[0]))
    g.db.commit()

    return {"msg": msg}, 200


@app.route('/delMsg/<int:id>',methods=['POST','DELETE'])
def delMsg(id):

    msg = g.db.execute(sql.get_msg_by_id(id)).fetchone()
    if (not msg):
        return "msg not found"

    oMsg = message(msg[1:])
    if (oMsg.sender != session["user"] and oMsg.receiver != session["user"]):
            return "this isnt your message", 401
    
    g.db.execute(sql.delete_message_by_id(id))
    g.db.commit()

    return "(: your message was deleted :)", 200


#endregion



#region errors


@app.errorhandler(TypeError)
def handle_type_error(error):
    return "bad parameters sent", 404


@app.route('/clearDB', methods=["GET","POST"])
def clearDB():

    g.db.execute("DELETE FROM messages WHERE True = True")
    g.db.commit()

    return "the DataBase is new now"


#endregion



#region classes and functions


def checkUserExist(name):
    userId = g.db.execute(sql.check_user_exist(name)).fetchone()
    return bool(userId)


def getUserId(name):
    sqlIdRows = g.db.execute(sql.get_user_id(name))
    for id in sqlIdRows:
        return id[0]
    

class message:
    def __init__(self, arrParams):
        self.sender        = arrParams[0]
        self.receiver      = arrParams[1]
        self.creation_date = arrParams[2]
        self.sbjct         = arrParams[3]
        self.msg           = arrParams[4]

    def toDict(self):
        return {"sender":self.sender,
                "receiver":self.receiver,
                "creation_date":self.creation_date,
                "sbjct":self.sbjct,
                "msg":self.msg}


#endregion



if __name__ == "__main__":
    app.debug = True
    host = os.environ.get('IP', config.IP)
    port = os.environ.get('PORT', config.PORT)
    app.run(host=host,port=port)

    

