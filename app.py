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

    g.db = sql.sql(config.DB_NAME)


@app.after_request
def after_request(response):
    if(hasattr(g, "db")):
        g.db.close()

    return response


@app.route('/login', methods=["GET","POST"])
def login():
    
    user = request.form['user'] 
    paswd = request.form['paswd']

    #validation
    valid = sql.validate()
    if (not(valid.isStrInput(user) and valid.isStrIntInput(paswd))):
        return "please enter valied input", 404

    if (not checkUserExist(user)):
        return "user " + user  + " unexist in the system", 404
    
    #simple sql injection check
    if (not ' ' in user):
        dbPasswd = g.db.login(user)
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

    subject = request.form['subject'] 
    content = request.form['content']

    valid = sql.validate()
    if (not (valid.isStrInput(toUsr) and
             valid.isFullTxtInput(subject) and
             valid.isFullTxtInput(content)
            )):
        return "please enter valied input", 404

    if (not checkUserExist(toUsr)):
        return "user " + toUsr  + " unexist in the system", 404
    elif (toUsr == session["user"]):
        return "dont talk to yourself", 404

    msg = message((session['user'], toUsr,
                   dt.now().strftime(config.DATE_FORMAT),
                   request.form['subject'], request.form['content']))

    g.db.insert_massage(msg)

    msgId = g.db.get_sent_msg_id()

    return "sent successfuly - msg number is " + str(msgId), 200


@app.route('/getMultyMsg/<string:fromUsr>/<int:visited>',methods=['GET','POST'])
def getMultyMsg(fromUsr,visited):

    valid = sql.validate()
    if (not (valid.isStrInput(fromUsr) and
             valid.isIntInput(visited) 
            )):
            return "please enter valied input", 404

    if (not checkUserExist(fromUsr)):
        return "user " + fromUsr  + " unexist in the system", 404
    elif (fromUsr == session["user"]):
        return "write name of someone else", 404

    Sender = fromUsr
    Me = session['user']

    msgs = g.db.get_all_msgs(Me, fromUsr, visited)

    if (not msgs):
        return "there are no " + ( "" if visited else "new ") + "messages", 204

    mailPack = {}
    for msg in msgs: 
        oMsg = message(msg[1:])
        mailPack['msgId ' + str(msg[0]) + ' content'] = oMsg.toDict()

    g.db.set_visited_all(Me, Sender)
    
    return mailPack 


@app.route('/getOneMsg/<string:sign>', methods=['GET','POST'])
def getOneMsg(sign):

    valid = sql.validate()
    if (not valid.isStrIntInput(sign)):
        return "please enter valied input", 404

    msg = None

    if (sign.isnumeric()):

        msg = g.db.get_msg_by_id(sign)
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
        
        msgs = g.db.get_all_msgs(session["user"],sign,True)

        if ( not msgs ):
            return "no msg from " + sign, 204

        # returm the last message sent by the user
        msg = max(msgs,key=lambda m: dt.strptime(message(m[1:]).creation_date,config.DATE_FORMAT))

    g.db.set_visited_one(msg[0])

    return {"msg": msg}, 200


@app.route('/delMsg/<int:id>',methods=['POST','DELETE'])
def delMsg(id):

    valid = sql.validate()
    if (not valid.isIntInput(id)):
            return "please enter valied input", 404

    msg = g.db.get_msg_by_id(id)
    if (not msg):
        return "msg not found", 204

    oMsg = message(msg[1:])
    if (oMsg.sender != session["user"] and oMsg.receiver != session["user"]):
            return "this isnt your message", 401
    
    g.db.delete_message_by_id(id)

    return "(: your message was deleted :)", 200


#endregion



#region maintaining


@app.errorhandler(TypeError)
def handle_type_error(error):
    return "bad parameters sent", 404


@app.route('/clearDB', methods=["GET","POST"])
def clearDB():

    g.db.db.execute("DELETE FROM messages WHERE True = True")
    g.db.db.commit()

    return "the DataBase is new now"


@app.route('/Apear/<user>', methods=["GET","POST"])
def Apear(user):
    
    return g.db.db.execute("select last_transaction, logged_in from users where user_name = " + user).fetchone()

#endregion



#region classes and functions


def checkUserExist(name):
    userId = g.db.check_user_exist(name)
    return bool(userId)


def getUserId(name):
    id = g.db.get_user_id(name)
    return id 
    

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


    

