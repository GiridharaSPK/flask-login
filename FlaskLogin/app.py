from flask import Flask, render_template, url_for
from flask_login import UserMixin
from flask import request, redirect
from werkzeug.utils import secure_filename
import sqlite3
import boto3

app = Flask(__name__)

conn = sqlite3.connect('database.db')
print("Opened database successfully");

# conn.execute('DROP TABLE user');
conn.execute('CREATE TABLE IF NOT EXISTS user (username TEXT, password TEXT, email EMAIL, first_name TEXT, last_name TEXT, link TEXT)');
print("Table created successfully");

app.config['S3_BUCKET'] = "storage-bucket-gr"
app.config['S3_KEY'] = "AKIAQV3DBC4HY46X23S5"
app.config['S3_SECRET'] = "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"
app.config['S3_LOCATION'] = 'http://{}.s3.us-east-2.amazonaws.com/'.format(app.config['S3_BUCKET'])

@app.route('/')
def init():
    return render_template('login.html')       

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
            f = request.files['file']
            s3 = boto3.client(
                "s3",
                aws_access_key_id=app.config['S3_KEY'],
                aws_secret_access_key=app.config['S3_SECRET']
            )
            s3.upload_fileobj(f, app.config['S3_BUCKET'], f.filename)

            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            fname = request.form['fname']
            lname = request.form['lname']
            link = app.config['S3_LOCATION']+f.filename
            
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO user (username,password,email,first_name,last_name, link) VALUES (?,?,?,?,?,?)",(username,password,email,fname,lname, link))
                con.commit()
            
            return render_template("home.html", result = [username, password, email, fname, lname, ])

        except BaseException as err:
            con.rollback()
            print(f"error in insert operation : Unexpected {err=}, {type(err)=}")
            con.close()
       
    return render_template("registration.html")

@app.route('/userdetails/<name>')
def user_home(name):
    # return f"Your name is {name}"
    return render_template("userdetails.html")

# @app.route('/uploader', methods = ['GET', 'POST'])
# def upload_file():
#     if(request.method == 'POST'):
#         f = request.files['file']
#         # f.save(secure_filename(f.filename))
#         # s3 = boto3.client('s3')
#         s3 = boto3.client(
#             "s3",
#             aws_access_key_id=app.config['S3_KEY'],
#             aws_secret_access_key=app.config['S3_SECRET']
#         )
#         BUCKET = "storage-bucket-gr"
#         s3.upload_fileobj(f, BUCKET, f.filename)
#         return 'file uploaded successfully'


if __name__ == '__main__':
    app.run(debug = True)
