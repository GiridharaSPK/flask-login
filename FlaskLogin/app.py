from flask import Flask, render_template, url_for
from flask_login import UserMixin
from flask import request, redirect
import sqlite3
# from flask_wtf import wtforms
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import InputRequired, Length, ValidationError


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///database.db'
# app.config['SECRET_KEY'] = 'mySecretKey'

conn = sqlite3.connect('database.db')
print("Opened database successfully");

# conn.execute('DROP TABLE user');
conn.execute('CREATE TABLE IF NOT EXISTS user (username TEXT, password TEXT, email EMAIL, first_name TEXT, last_name TEXT)');
print("Table created successfully");

@app.route('/')
def init():
    return render_template('login.html')

@app.route('/table')
def see_table():
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        result = cur.execute("SELECT count(*) FROM user")
    return render_template("table.html", result = result)        

@app.route('/login', methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE username = ? AND password = ?",(username,password))
        result = cur.fetchone()
        # con.commit()
    if(result):
        return render_template("home.html", result = result)
    return render_template("login.html", error_flag = True)

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            fname = request.form['fname']
            lname = request.form['lname']

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO user (username,password,email,first_name,last_name) VALUES (?,?,?,?,?)",(username,password,email,fname,lname))
                con.commit()
            return render_template("home.html", result = [username, password, email, fname, lname])
            
        except BaseException as err:
            con.rollback()
            print(f"error in insert operation : Unexpected {err=}, {type(err)=}")
            # raise
            # return render_template("registration.html")
            con.close()

            # return redirect(f"/userdetails/{username}")
    return render_template("registration.html")

@app.route('/userdetails/<name>')
def user_home(name):
    # return f"Your name is {name}"
    return render_template("userdetails.html")

if __name__ == '__main__':
    app.run(debug = True)
