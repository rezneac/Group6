import os
import PIL
import json
import google.generativeai as genai

from flask import Flask, render_template, jsonify, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

from models import User, SavingsGoal, Contribution, Cart, Item, db

genai.configure(api_key="AIzaSyBPlLN0RvHJQlCB8mBFVzE0aHCQlX_HFVg")
client = genai.GenerativeModel('gemini-2.0-flash')

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'super_secret_key'  # Change this in production!
app.config['file_extensions'] = ['.jpeg', '.jpg', '.png']

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

### Authentication Navigation Routes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    newcart = Cart()
    db.session.add(newcart)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")  # Serve login form

    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

### Savings Goals Navigation Routes

@app.route('/set_goal', methods=['POST'])
@login_required
def set_goal():
    goal_name = request.form.get('goal_name')
    target_amount = request.form.get('target_amount')

    if not target_amount or float(target_amount) <= 0:
        return jsonify({"error": "Please provide a valid target amount."}), 400

    target_amount = float(target_amount)
    existing_goal = current_user.goal

    if existing_goal:
        existing_goal.name = goal_name
        existing_goal.target_amount = target_amount
    else:
        new_goal = SavingsGoal(name=goal_name, target_amount=target_amount)
        db.session.add(new_goal)
        current_user.goal = new_goal
    
    db.session.commit()
    return redirect("/progress")


# Join forces with another person to contribute towards their goal as well.
@app.route('/share_goal', methods=['POST'])
@login_required
def share_goal():
    share_code = request.form.get('share-code')
    
    if not share_code:
        return jsonify({"error": "Invalid share code."}), 400
    
    # Find the goal associated with the share code
    shared_goal = SavingsGoal.query.filter_by(id=share_code).first()
    
    if not shared_goal:
        return jsonify({"error": "Goal not found."}), 404
    
    # Update the current user's goal
    current_user.goal = shared_goal
    db.session.commit()
    
    return redirect("/progress")

@app.route('/add_contribution', methods=['POST'])
@login_required
def add_contribution():
    contribution_amount = request.form.get('contribution_amount')

    if not contribution_amount or float(contribution_amount) <= 0:
        return jsonify({"error": "Please provide a valid contribution amount."}), 400

    contribution = Contribution(user=current_user, amount=float(contribution_amount))
    db.session.add(contribution)
    db.session.commit()
    return redirect("/progress")

@app.route('/savings', methods=['GET'])
@login_required
def get_savings_by_user():
    goal = current_user.goal
    if not goal:
        return jsonify({"error": "User has no savings goal assigned"}), 404

    users = User.query.filter_by(goal_id=goal.id).all()
    user_savings = [{
        "username": user.username,
        "saved_amount": sum(c.amount for c in user.contributions),
        "progress": sum(c.amount for c in user.contributions) / goal.target_amount * 100 if goal.target_amount else 0,
        "contributions": [{"amount": c.amount, "date": c.date, "username": c.user.username} for c in user.contributions]
    } for user in users]

    return jsonify({
        "goal": {"id": goal.id, "name": goal.name, "target_amount": goal.target_amount},
        "users": user_savings
    }), 200

### Receipt Navigation Routes

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

                response = client.generate_content(
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

### General Navigation Routes

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/faqs', methods=['GET'])
def faqs():
    return render_template("faqs.html")

@app.route('/signup', methods=['GET'])
def signup():
    return render_template("signup.html")

@app.route('/cart', methods=['GET'])
@login_required
def cart():
    return render_template("cart.html")

@app.route('/progress')
@login_required
def progress():
    """ Serve the savings progress page (if logged in), else redirect to login. """
    return render_template('progress.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)