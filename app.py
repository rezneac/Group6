import base64
from datetime import datetime
from google import genai
from google.genai import types
import hashlib

client = genai.Client(api_key="API_KEY")

import json
import PIL.Image

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os
from sqlalchemy.orm import joinedload

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
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
    contributions = dbs.relationship('Contribution', backref='user', lazy='dynamic')


class Item(dbs.Model, UserMixin):
    id = dbs.Column(dbs.Integer, primary_key=True)
    name = dbs.Column(dbs.String(50), nullable=False)
    price = dbs.Column(dbs.Integer, nullable=False)
    cart_id = dbs.Column(dbs.Integer, dbs.ForeignKey('cart.id'))



class Contribution(dbs.Model, UserMixin):
    id = dbs.Column(dbs.Integer, primary_key=True)
    amount = dbs.Column(dbs.Integer, nullable=False)
    user_id = dbs.Column(dbs.Integer, dbs.ForeignKey('user.id'), nullable=False)
    savings_id = dbs.Column(dbs.Integer, dbs.ForeignKey('savings.id'), nullable=False)


class Savings(dbs.Model, UserMixin):
    id = dbs.Column(dbs.Integer, primary_key=True)
    hash = dbs.Column(dbs.String(50), nullable=False)
    name = dbs.Column(dbs.String(50), nullable=False)
    savingsGoal = dbs.Column(dbs.Integer, nullable=False)
    contributions = dbs.relationship('Contribution', backref='savings', lazy='dynamic')


class Cart(dbs.Model):
    id = dbs.Column(dbs.Integer, primary_key=True)
    items = dbs.relationship('Item', lazy='dynamic')


with app.app_context():
    dbs.create_all()


class Registerform(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validusername(self, username):
        existingusername = User.query.filter_by(username=username.data).first()

        if existingusername:
            raise ValidationError("username already exist you cant use this")


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

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('signup'))

        hashedpassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        newuser = User(username=form.username.data, password=hashedpassword)
        dbs.session.add(newuser)
        dbs.session.commit()

        newcart = Cart()
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
def dashboard():
    savings = Savings.query.join(Contribution).filter(Contribution.user_id == current_user.id).order_by(Savings.name).all()# Assuming you want to filter Savings based on contributions made by the current user


    return render_template("progress1.html", objs=savings)

@app.route("/set_goal", methods=['GET', 'POST'])
@login_required
def set_goal():
    if request.method == 'POST':
        name = request.form.get('goal_name')
        goal = request.form.get('target_amount')
        initial = request.form.get('initial_contribution')

        # Create the Savings instance without the hash
        new_savings = Savings(name=name, hash='', savingsGoal=goal)
        print(new_savings)
        print(new_savings)
        print(new_savings)
        dbs.session.add(new_savings)
        dbs.session.commit()

        # Update the hash attribute with the MD5 hash of the id
        new_savings.hash = hashlib.md5(str(new_savings.id).encode()).hexdigest()
        dbs.session.commit()

        # Create the Contribution instance
        contribution = Contribution(amount=initial, user_id=current_user.id, savings_id=new_savings.id)
        dbs.session.add(contribution)
        dbs.session.commit()

        return redirect(url_for('dashboard'))
    savings = Savings.query.join(Contribution).filter(Contribution.user_id == current_user.id).order_by(Savings.name).all()

    return render_template("progress1.html", objs=savings)

@app.route("/addfriendsavings", methods=['GET', 'POST'])
#@login_required
def addfriendsavings():
    savings = Savings.query.join(Contribution).filter(Contribution.user_id == current_user.id).order_by(Savings.name).all()# Assuming you want to filter Savings based on contributions made by the current user  # Initialize obj to an empty dictionary

    return render_template("progress1.html", objs=savings)
@app.route("/dashboard", methods=['GET', 'POST'])
#@login_required
def deletesavings():
    savings = Savings.query.join(Contribution).filter(Contribution.user_id == current_user.id).order_by(Savings.name).all()# Assuming you want to filter Savings based on contributions made by the current user  # Initialize obj to an empty dictionary

    return render_template("progress1.html", objs=savings)

@app.route("/add_contribution", methods=['GET', 'POST'])
#@login_required
def add_contribution():
    savings = Savings.query.join(Contribution).filter(Contribution.user_id == current_user.id).order_by(Savings.name).all()# Assuming you want to filter Savings based on contributions made by the current user  # Initialize obj to an empty dictionary

    return render_template("progress1.html", objs=savings)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)

                return redirect(url_for('dashboard'))
    return render_template("login1.html", form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


app.run(debug=True, port=8000)
