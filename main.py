import smtplib
from email.mime.text import MIMEText
import nltk
nltk.download("punkt")
from nltk.tokenize import word_tokenize
from nltk.stem import LancasterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from flask import redirect, session
from flask import render_template, url_for
import firebase_admin
import random
from flask import Flask, request
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter
from google.cloud.firestore_v1 import FieldFilter
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
app = Flask(__name__)
app.secret_key="Phising@12345"
message_x=""
#classifier=""
def datafile():
    data = pickle.load(open("training_data.pkl","rb"))
    message_x = data["message_x"]
    classifier = data["classifier"]

lstem = LancasterStemmer()
tfvec=TfidfVectorizer(stop_words='english')
datafile()

@app.route('/usersendmail')
def usersendmail():
    try:
        id = session['userid']
        db = firestore.client()
        docs = (
            db.collection("newuser")
                .where(filter=FieldFilter("id", "!=", id))
                .stream())
        data=[]
        for doc in docs:
            print(f"{doc.id} => {doc.to_dict()}")
            data.append(doc.to_dict()['EmailId'])
        return render_template("usersendmail.html",data=data)
    except Exception as e:
        return str(e)


def bow(message):
    data = pickle.load(open("training_data.pkl", "rb"))
    message_x = data["message_x"]
    classifier = data["classifier"]
    mess_t = tfvec.fit(message_x)
    message_test = mess_t.transform(message).toarray()
    return message_test

def mess(messages):
    message_x = []
    for me_x in messages:
        me_x = ''.join(filter(lambda mes: (mes.isalpha() or mes == " "), me_x))
        words = word_tokenize(me_x)
        message_x += [' '.join([lstem.stem(word) for word in words])]
    return message_x

sender = "dhanu.innovation@gmail.com"
password = "dkgppiexjwbznzcv"

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

@app.route('/')
def homepage():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/index')
def indexpage():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/logout')
def logoutpage():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/about')
def aboutpage():
    try:
        return render_template("about.html")
    except Exception as e:
        return str(e)

@app.route('/services')
def servicespage():
    try:
        return render_template("services.html")
    except Exception as e:
        return str(e)

@app.route('/gallery')
def gallerypage():
    try:
        return render_template("gallery.html")
    except Exception as e:
        return str(e)

@app.route('/adminlogin')
def adminloginpage():
    try:
        return render_template("adminlogin.html",msg="")
    except Exception as e:
        return str(e)

@app.route('/userlogin', methods=['POST','GET'])
def userloginpage():
    try:
        msg=""
        if request.method == 'POST':
            uname = request.form['uname']
            pwd = request.form['pwd']
            db = firestore.client()
            newdb_ref = db.collection('newuser')
            dbdata = newdb_ref.get()
            data = None
            flag = False
            status=False
            for doc in dbdata:
                # print(doc.to_dict())
                # print(f'{doc.id} => {doc.to_dict()}')
                # data.append(doc.to_dict())
                data = doc.to_dict()
                if (data['UserName'] == uname and data['Password'] == pwd):
                    flag = True
                    session['userid'] = data['id']
                    status=data['Status']
                    break
            if (flag and status):
                return render_template("usermainpage.html")
            elif(flag and not status):
                return render_template("userlogin.html", msg="You are blocked for violation of Rules")
            else:
                return render_template("userlogin.html", msg="UserName/Password is Invalid")
        else:
            return render_template("userlogin.html", msg=msg)
    except Exception as e:
        return render_template("userlogin.html", msg=e)

@app.route('/stafflogin')
def staffloginpage():
    try:
        return render_template("stafflogin.html")
    except Exception as e:
        return str(e)

@app.route('/newuser')
def newuser():
    try:
        msg=""
        return render_template("newuser.html", msg=msg)
    except Exception as e:
        return str(e)

@app.route('/addnewuser', methods=['POST'])
def addnewuser():
    try:
        print("Add New User page")
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['emailid']
            phnum = request.form['phonenumber']
            address = request.form['address']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'FirstName': fname,'LastName':lname,
                    'UserName': uname,'Password':pwd,
                    'EmailId': email,'PhoneNumber':phnum,
                    'Address': address, 'Status':True}
            db = firestore.client()
            newuser_ref = db.collection('newuser')
            id = json['id']
            newuser_ref.document(id).set(json)
        return render_template("newuser.html", msg="New User Added Success")
    except Exception as e:
        return str(e)

@app.route('/addnewstaff', methods=['POST'])
def addnewstaff():
    try:
        print("Add New Staff page")
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uname = request.form['uname']
            pwd = request.form['pwd']
            email = request.form['email']
            phnum = request.form['phonenumber']
            address = request.form['address']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'FirstName': fname,'LastName':lname,
                    'UserName': uname,'Password':pwd,
                    'EmailId': email,'PhoneNumber':phnum,
                    'Address': address}
            db = firestore.client()
            newuser_ref = db.collection('newstaff')
            id = json['id']
            newuser_ref.document(id).set(json)
        return render_template("adminaddstaff.html", msg="New Staff Added Success")
    except Exception as e:
        return str(e)

def getidbyemailid(emailid):
    try:
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        id=0
        for doc in userdata:
            if doc.to_dict()['EmailId']==emailid:
                id=doc.to_dict()['id']
                break
    except Exception as e:
        return str(e)
    return id

@app.route('/usersendingmail', methods=['POST'])
def usersendingmail():
    try:
        if request.method == 'POST':
            print("User Sending Mail")
            data = pickle.load(open("training_data.pkl", "rb"))
            message_x = data["message_x"]
            classifier = data["classifier"]
            senderid = session['userid']
            db = firestore.client()
            newdb_ref = db.collection('newuser')
            data = newdb_ref.document(senderid).get().to_dict()
            senderemail=data["EmailId"]
            subject = request.form['subject']
            body = request.form['body']
            receiveremailid = request.form['receiveremailid']
            receiverid=getidbyemailid(receiveremailid)
            data = newdb_ref.document(receiverid).get().to_dict()
            id = str(random.randint(1000, 9999))
            msg = body
            # preprocess the message
            message = mess([msg])
            spam_not = "NotSpam"
            if classifier.predict(bow(message)):
                spam_not="Spam"
            print("Span/Not : ",spam_not)
            json = {'id': id,
                    'Subject': subject,'Body':body,
                    'ReceiverId': receiverid,'ReceiverEmail': receiveremailid,
                    'SenderId':senderid,'SenderEmail':senderemail,"Spam_Not":spam_not}
            db = firestore.client()
            newuser_ref = db.collection('newemail')
            id = json['id']
            newuser_ref.document(id).set(json)

            id = session['userid']
            db = firestore.client()
            docs = (db.collection("newuser").where(filter=FieldFilter("id", "!=", id)).stream())
            data = []
            for doc in docs:
                print(f"{doc.id} => {doc.to_dict()}")
                data.append(doc.to_dict()['EmailId'])
        return render_template("usersendmail.html", msg="Mail Send Success", data=data)
    except Exception as e:
        return str(e)

@app.route('/contact',methods=['POST','GET'])
def contactpage():
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            subject = request.form['subject']
            message = request.form['message']
            id = str(random.randint(1000, 9999))
            json = {'id': id,
                    'ContactName': name,
                    'Message': message, 'Subject': subject,
                    'EmailId': email}
            db = firestore.client()
            db_ref = db.collection('newcontact')
            id = json['id']
            db_ref.document(id).set(json)
            msg="Contact Added Success"
            return render_template("contact.html",msg=msg)
        else:
            return render_template("contact.html")
    except Exception as e:
        return str(e)
""""
@app.route('/usersendmail')
def usersendmail():
    try:
        id = session['userid']
        db = firestore.client()
        docs = (
            db.collection("newuser")
                .where(filter=FieldFilter("id", "!=", id))
                .stream())
        data=[]
        for doc in docs:
            print(f"{doc.id} => {doc.to_dict()}")
            data.append(doc.to_dict()['EmailId'])
        return render_template("usersendmail.html",data=data)
    except Exception as e:
        return str(e)
"""
@app.route('/adminlogincheck', methods=['POST'])
def adminlogincheck():
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']
    print("Uname : ", uname, " Pwd : ", pwd);
    if uname == "admin" and pwd == "admin":
        return render_template("adminmainpage.html")
    else:
        return render_template("adminlogin.html", msg="UserName/Password is Invalid")

@app.route('/userviewprofile')
def userviewprofile():
    try:
        id=session['userid']
        print("Id",id)
        db = firestore.client()
        newdb_ref = db.collection('newuser')
        data = newdb_ref.document(id).get().to_dict()
        print(data)
        return render_template("userviewprofile.html", data=data)
    except Exception as e:
        return str(e)
        return render_template("userlogin.html", msg=e)

@app.route('/staffviewprofile')
def staffviewprofile():
    try:
        id=session['staffid']
        print("Id",id)
        db = firestore.client()
        newdb_ref = db.collection('newstaff')
        data = newdb_ref.document(id).get().to_dict()
        print(data)
        return render_template("staffviewprofile.html", data=data)
    except Exception as e:
        return str(e)
        return render_template("stafflogin.html", msg=e)

"""
@app.route('/userlogincheck', methods=['POST'])
def userlogincheck():
    try:
        if request.method == 'POST':
            uname = request.form['uname']
            pwd = request.form['pwd']
            db = firestore.client()
            print("Uname : ", uname, " Pwd : ", pwd);
            newdb_ref = db.collection('newuser')
            dbdata = newdb_ref.get()
            data = []
            flag = False
            for doc in dbdata:
                data = doc.to_dict()
                if(data['UserName']==uname and data['Password']==pwd):
                    flag=True
                    session['userid']=data['id']
                    break
            if(flag):
                print("Login Success")
                return render_template("usermainpage.html")
            else:
                return render_template("userlogin.html", msg="UserName/Password is Invalid")
    except Exception as e:
        return str(e)
        return render_template("userlogin.html", msg=e)
"""

@app.route('/stafflogincheck', methods=['POST'])
def stafflogincheck():
    try:
        if request.method == 'POST':
            uname = request.form['uname']
            pwd = request.form['pwd']
            db = firestore.client()
            print("Uname : ", uname, " Pwd : ", pwd);
            newdb_ref = db.collection('newstaff')
            dbdata = newdb_ref.get()
            data = []
            flag = False
            for doc in dbdata:
                data = doc.to_dict()
                if(data['UserName']==uname and data['Password']==pwd):
                    flag=True
                    session['staffid']=data['id']
                    break
            if(flag):
                print("Login Success")
                return render_template("staffmainpage.html")
            else:
                return render_template("stafflogin.html", msg="UserName/Password is Invalid")
    except Exception as e:
        return str(e)
        return render_template("stafflogin.html", msg=e)

@app.route('/adminmainpage')
def adminmainpage():
    try:
        return render_template("adminmainpage.html")
    except Exception as e:
        return str(e)

@app.route('/adminaddstaff')
def adminaddstaffpage():
    try:
        return render_template("adminaddstaff.html")
    except Exception as e:
        return str(e)

@app.route('/adminviewstaffs')
def adminviewstaffspage():
    try:
        db = firestore.client()
        newstaff_ref = db.collection('newstaff')
        staffdata = newstaff_ref.get()
        data=[]
        for doc in staffdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        print("Staff Data " , data)
        return render_template("adminviewstaffs.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewusers')
def adminviewuserspage():
    try:
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        print("Staff Data ", data)
        return render_template("adminviewusers.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewcontacts')
def adminviewcontacts():
    try:
        db = firestore.client()
        dbref = db.collection('newcontact')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        return render_template("adminviewcontacts.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/staffviewusers')
def staffviewusers():
    try:
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = []
        for doc in userdata:
            print(doc.to_dict())
            print(f'{doc.id} => {doc.to_dict()}')
            data.append(doc.to_dict())
        return render_template("staffviewusers.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/staffviewreports')
def staffviewreports():
    try:
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        data = []
        userids=[]
        for doc in userdata:
            userids.append(doc.to_dict()['id'])

        dbref = db.collection('newemail')
        dbdata = dbref.get()
        emaildata = []
        for doc in dbdata:
            emaildata.append(doc.to_dict())

        datapoints = []
        cnt=10
        for id in userids:
            spamcnt=0
            temp={}
            for doc in emaildata:
                if doc['SenderId']==id and doc['Spam_Not']=='Spam':
                    spamcnt+=1
            temp['x']=cnt
            temp['y']=spamcnt
            cnt+=10
            datapoints.append(temp)

        datapoints2 = []
        cnt=10
        for id in userids:
            spamcnt = 0
            temp = {}
            for doc in emaildata:
                if doc['SenderId'] == id and doc['Spam_Not'] == 'NotSpam':
                    spamcnt += 1
            temp['x'] = cnt
            temp['y'] = spamcnt
            cnt += 10
            datapoints2.append(temp)
        print("Data Points  : ", datapoints)
        print("Data Points2 : ", datapoints2)
        x=0
        data=[]
        for x in range(0, len(userids)):
            temp={}
            temp['id']=userids[x]
            temp['spam'] = datapoints[x]['y']
            temp['notspam'] = datapoints2[x]['y']
            data.append(temp)

        return render_template("staffviewreports.html", data=data,
                               datapoints=datapoints, datapoints2=datapoints2)
    except Exception as e:
        return str(e)



@app.route('/userviewsendmails')
def userviewsendmails():
    try:
        id = session['userid']
        db = firestore.client()
        dbref = db.collection('newemail')
        dbdata = dbref.get()
        data = []
        for doc in dbdata:
            if doc.to_dict()['SenderId']==id:
                data.append(doc.to_dict())
        return render_template("userviewsendmails.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/userviewreceivedmails')
def userviewreceivedmails():
    try:
        id = session['userid']
        db = firestore.client()
        dbref = db.collection('newemail')
        dbdata = dbref.get()
        data = []
        for doc in dbdata:
            if doc.to_dict()['ReceiverId']==id:
                data.append(doc.to_dict())
        return render_template("userviewreceivermails.html", data=data)
    except Exception as e:
        return str(e)

@app.route('/adminviewreports')
def adminviewreports():
    try:
        db = firestore.client()
        dbref = db.collection('newemail')
        dbdata = dbref.get()
        data = {}
        spamcnt=0
        notspam=0
        for doc in dbdata:
            if(doc.to_dict()['Spam_Not']=='Spam'):
                spamcnt+=1
            else:
                notspam += 1
        data['Spam']=spamcnt
        data['NotSpam'] = notspam
        graphdata = [
    { "label": "Spam", "y": spamcnt },
    { "label": "NotSpam", "y": notspam }]
        return render_template("adminviewreports.html", data=data, graphdata=graphdata)
    except Exception as e:
        return str(e)

@app.route('/userviewreports')
def userviewreports():
    try:
        id = session['userid']
        db = firestore.client()
        dbref = db.collection('newemail')
        dbdata = dbref.get()
        data = {}
        spamcnt=0
        notspam=0
        for doc in dbdata:
            if doc.to_dict()['SenderId']==id:
                if(doc.to_dict()['Spam_Not']=='Spam'):
                    spamcnt+=1
                else:
                    notspam += 1
        data['Spam']=spamcnt
        data['NotSpam'] = notspam
        graphdata = [
    { "label": "Spam", "y": spamcnt },
    { "label": "NotSpam", "y": notspam }]
        return render_template("userviewreports.html", data=data, graphdata=graphdata)
    except Exception as e:
        return str(e)

@app.route('/staffblockusers')
def staffblockusers():
    try:
        db = firestore.client()
        dbref = db.collection('newuser')
        userdata = dbref.get()
        user_data = []
        for doc in userdata:
            temp={}
            tempdata = doc.to_dict()
            if(tempdata['Status'] == True):
                temp['UserId']= tempdata['id']
                temp['FirstName'] = tempdata['FirstName']
                temp['LastName'] = tempdata['LastName']
                temp['EmailId'] = tempdata['EmailId']
                temp['PhoneNumber'] = tempdata['PhoneNumber']
                temp['Address'] = tempdata['Address']
                #userids.append(doc.to_dict()['id'])
                user_data.append(temp)

        print("User Data : \n", user_data)

        dbref = db.collection('newemail')
        dbdata = dbref.get()
        emaildata = []
        for doc in dbdata:
            emaildata.append(doc.to_dict())

        print("Email Data : \n", emaildata)
        for id in user_data:
            notspamcnt,spamcnt=0,0
            for doc in emaildata:
                if doc['SenderId']==id['UserId'] and doc['Spam_Not']=='Spam':
                    spamcnt+=1
                if doc['SenderId']==id['UserId'] and doc['Spam_Not']=='NotSpam':
                    notspamcnt+=1
            id['SpanCnt']=spamcnt
            id['NotSpanCnt'] = notspamcnt

        print("User Data    : ", user_data)
        return render_template("staffblockusers.html", data=user_data)
    except Exception as e:
        return str(e)

@app.route('/staffblockusers1', methods=["POST","GET"])
def staffblockusers1():
    try:
        userid = request.args['id']
        emailid = request.args['emailid']
        db = firestore.client()
        data_ref = db.collection(u'newuser').document(userid)
        data_ref.update({u'Status': False})
        subject="Your Email is blocked"
        body="Your Email is blocked due to violation of Rules"
        recipients=[emailid]
        send_email(subject, body, sender, recipients, password)
        return redirect(url_for("staffblockusers"))
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.debug = True
    app.run()