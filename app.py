import base64
from datetime import datetime
from google import genai
from google.genai import types

client = genai.Client(api_key="API_KEY")

import json
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

with app.app_context():
    dbs.create_all()


class User(dbs.Model, UserMixin):
    id = dbs.Column(dbs.Integer, primary_key=True)
    username = dbs.Column(dbs.String(20), nullable=False, unique=True)
    password = dbs.Column(dbs.String(80), nullable=False)
    contributions = dbs.relationship('Contribution')


class Item(dbs.Model, UserMixin):
    id = dbs.Column(dbs.Integer, primary_key=True)
    name = dbs.Column(dbs.String(50), nullable=False)
    price = dbs.Column(dbs.Integer, nullable=False)
    cart_id = dbs.Column(dbs.Integer, dbs.ForeignKey('cart.id'))



class Contribution(dbs.Model, UserMixin):
    id = dbs.Column(dbs.Integer, primary_key=True)
    amount = dbs.Column(dbs.Integer, nullable=False)
    user_id = dbs.Column(dbs.Integer, dbs.ForeignKey('user.id'), nullable=False)



class Savings(dbs.Model, UserMixin):
    id = dbs.Column(dbs.Integer, primary_key=True)
    hash = dbs.Column(dbs.String(50), nullable=False)
    name = dbs.Column(dbs.String(50), nullable=False)
    savingsGoal = dbs.Column(dbs.Integer, nullable=False)
    contributions = dbs.relationship('contribution', lazy='dynamic')


class Cart(dbs.Model):
    id = dbs.Column(dbs.Integer, primary_key=True)
    items = dbs.relationship('item', lazy='dynamic')


with app.app_context():
    dbs.create_all()


class commentform(FlaskForm):
    comment = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Comment..."})
    postid = StringField()
    submit = SubmitField("comment")


class Registerform(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validusername(self, username):
        existingusername = User.query.filter_by(username=username.data).first()

        if existingusername:
            raise ValidationError("username already exist you cant use this soz")


class Loginform(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
                             render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = Registerform()
    contribution = Contribution()

    if form.validate_on_submit():
        hashedpassword = bcrypt.generate_password_hash(form.password.data)

        newuser = User(username=form.username.data, password=hashedpassword , contributions=[contribution])
        newcart = Cart()
        dbs.session.add(newuser)
        dbs.session.commit()
        dbs.session.add(newcart)
        dbs.session.commit()
        return redirect(url_for('login'))

    return render_template("signup.html", form=form)


@app.route("/receipt", methods=['GET', 'POST'])
@login_required
def shoppinglist():
    obj = {}  # Initialize obj to an empty dictionary
    saved = Cart.items
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
                        "What is this image? Break down every position also show how many times each product is bought, containing name and price only! ALSO can you find one cheaper alternative to each item from uk supermarket stores. And make sure when you check for cheaper alternatives you look only to unit price for 1. PLEASE GIVE ONLY WHAT I REQUESTED IN JSON FORMAT WITH NOTHING BEFORE OR AFTER THE START AND END CURLY BRACKETS WITH THE NAMES AND PRICES FROM THE IMAGE AS, receipt_items, AND MAKE SURE YOU CALL THE CHEAPER ITEMS AS, alternative_items, WITH THE ALTERNATIVES' NAMES AND PRICES with a quantity column matching the reciepts one!!! HOWEVER IF YOU DO NOT RECOGNISE THE IMAGE TO BE A RECIEPT, RETURN AN ERROR JSON",
                        image])

                r = response.text

                for i in range(0, 50):
                    if r[i] == "{":
                        r = r[i:]
                        break

                r = r[:r.rfind('}') + 1]

                print(r)
                obj = json.loads(r)
                # item = Item(name = item.name,
                #             price = item.price,
                #             cart_id=cart_id)
                # dbs.session.add(item)
                # dbs.session.commit()

    return render_template("receipt.html", obj=obj, saved=saved)

@app.route("/dashboard", methods=['GET', 'POST'])
#@login_required
def savings():
    obj = Savings.query.filter_by(Savings.contributions.contains(User.contributions)).order_by(Savings.name).all()# Initialize obj to an empty dictionary


    return render_template("receipt.html", obj=obj, saved=saved)
@app.route("/dashboard", methods=['GET', 'POST'])
#@login_required
def newsavings():
    obj = {}  # Initialize obj to an empty dictionary

    return render_template("receipt.html", obj=obj, saved=saved)

@app.route("/dashboard", methods=['GET', 'POST'])
#@login_required
def addfriendsavings():
    obj = {}  # Initialize obj to an empty dictionary

    return render_template("receipt.html", obj=obj, saved=saved)
@app.route("/dashboard", methods=['GET', 'POST'])
#@login_required
def deletesavings():
    obj = {}  # Initialize obj to an empty dictionary

    return render_template("receipt.html", obj=obj, saved=saved)

@app.route("/dashboard", methods=['GET', 'POST'])
#@login_required
def contribute():
    obj = {}  # Initialize obj to an empty dictionary

    return render_template("receipt.html", obj=obj, saved=saved)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)

                return redirect(url_for('index'))
    return render_template("login1.html", form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


app.run(debug=True, port=8000)
