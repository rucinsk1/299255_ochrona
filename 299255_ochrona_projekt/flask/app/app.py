
import redis
import sqlalchemy
import math
from passlib.hash import bcrypt
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import session
from flask import Flask, redirect, url_for, render_template, request, session
import time
from flask_wtf.csrf import CSRFProtect
import socket
from sqlalchemy.sql import exists
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
import os



app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

app.secret_key ="89Twj1Ulzy4wFzOaDbiIsO2dmsZYmK5c9TT0x6nCsA8"#os.environ.get("SESSION_SECRET") #"1233125" #os.environ.get("SESSION_SECRET")
#app.permanent_session_lifetime=180
csrf = CSRFProtect(app)
app.config["PERMANENT_SESSION_LIFETIME"] = 300
banned_ip = []

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200))

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1024), unique=True, nullable=False)
    permission = db.Column(db.String(200))


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        time.sleep(1)
        session['counter'] += 1
        username = request.form['username']
        password = request.form['password']
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        if (username == 'admin'):
            print("Honeyspot")
        if (session['counter']>=5):
            #time.sleep(300)
            session['ip'] =host_ip
            banned_ip.append(host_ip)
            return redirect(url_for("ban"))

        if(db.session.query(User.query.filter(User.login == username).exists()).scalar() and bcrypt.verify(password, User.query.filter(User.login == username).first().password)):
            session['username'] = username
            session.permanent = True
            return redirect(url_for("user", name=username))
        else:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            if host_ip in banned_ip:
                session['ip']=host_ip
                return redirect(url_for("ban"))


            return render_template("index.html",  content = 10 -session['counter'])


        #if znajduje sie w bazie to przekieruj
        #register = request.form['register']
        #print(register)

    else:
        session['counter'] = 0;
        return render_template("index.html", content = 10 -session['counter'])

@app.route("/user", methods=["POST", "GET"])
def user():
    #jeżeli jest w bazie danych po submicie
    if request.method == "POST":
        session.clear()
        return redirect(url_for("home"))
    else:
        public_notes = []
        private_notes = []
        notes = db.session.query(Note)
        for note in notes:
            if note.permission == 'public':
                public_notes.append(note.content)
            if note.permission == session['username']:
                private_notes.append(note.content)
        return render_template("user.html", content = session['username'], public_notes=public_notes, private_notes=private_notes)





@app.route("/register", methods=["POST", "GET"])
def register():
    #jeżeli jest w bazie danych po submicie
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        users = db.session.query(User)
        logins_taken = []
        for user in users:
            logins_taken.append(user.login)

        if username in logins_taken:
            return render_template("register.html", content="Username already taken!")

        if password != password2:
            return render_template("register.html", content="passwords does not match!")

        if entropy(password) <= 3:
            return render_template("register.html", content="password is too weak!")




        if(password == password2 and entropy(password)>3 and username != 'admin'):
            bcrypted_pass = bcrypt.hash(password)
            user=User(login = username, password = bcrypted_pass)
            db.session.add(user)
            db.session.commit()
        return redirect(url_for("home")) #tutaj coś musi działać inaczej
    else:
        return render_template("register.html", content="")

@app.route("/note", methods=["POST", "GET"])
def note():
    if request.method == "POST":
        content = request.form['content']
        ispublic = request.form.getlist('public')

        if len(ispublic) >0:
            permission = 'public'
        else:
            permission = session['username']

        #encrypted_note = bcrypt.hash(content)
        note = Note(content = content, permission = permission)
        db.session.add(note)
        db.session.commit()

        return redirect(url_for("user", name = session['username']))  # tutaj coś musi działać inaczej
    else:
        return render_template("note.html", content =session['username'])

@app.route("/ban", methods=["GET"])
def ban():
    return render_template("ban.html", content =session['ip'])



def entropy(d):
   stat={}
   for c in d:
       m=c
       if m in stat:
           stat[m] +=1
       else:
           stat[m]=1
   H=0.0
   for i in stat.keys():
       pi=stat[i]/len(d)
       H -=pi*math.log2(pi)
   return H





if __name__ == "__main__":
     app.run()




