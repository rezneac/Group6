import base64
from datetime import datetime
from google import genai
from google.genai import types
client = genai.Client(api_key="keu")

import PIL.Image

from flask import Flask, render_template, url_for, redirect, request
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'
app.config['file_extensions'] = ['.jpeg', '.jpg', '.png']



dbs = SQLAlchemy(app)
bcrypt = Bcrypt(app)

loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.login_view = "login"

@loginmanager.user_loader
def loaduser(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("home.html")

class User(dbs.Model, UserMixin):
    id = dbs.Column(dbs.Integer, primary_key=True)
    username = dbs.Column(dbs.String(20), nullable=False, unique=True)
    password = dbs.Column(dbs.String(80), nullable=False)
    savings = dbs.Column(dbs.Integer, nullable=False)
    savingsGoal = dbs.Column(dbs.Integer, nullable=False)



@app.route("/post", methods=['GET', 'POST'])
#@login_required
def shoppinglist():
    if request.method == 'POST':
        uploadedfile = request.files['file']

        filename = uploadedfile.filename
        if filename != "":
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['file_extensions']:
                return redirect(url_for('shoppinglist'))
            else:
                #uploadedfile.save(os.path.join(app.root_path, 'static', 'images', 'reciept.'+file_ext))
                #newpost = Post(caption=caption, data=data,  pdata=current_user.pfp,
                  #             pname=current_user.username, postdate=datetime.now().replace(microsecond=0))
                image = PIL.Image.open(uploadedfile)

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        "What is this image? Break down every position also show how many times each product is bought, containing name ,price only and the lowes and highest price of an item! PLEASE GIVE ONLY WHAT I REQUESTED AS A JSON FILE!!! ALSO can you findcheaper alternatives to each item from uk supermarket stores. HOWEVER IF YOU DO NOT RECOGNISE THE IMAGE TO BE A RECIEPT, RETURN AN ERROR JSON",
                        image])

                print(response.text)

                return redirect(url_for('shoppinglist'))

    return render_template("post.html")

app.run(debug=True, port=8000)