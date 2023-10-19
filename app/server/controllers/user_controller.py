from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from server import app
from server.models.user import User
from server.forms.user_forms import LoginForm, SignupForm
from server.models.mongodb import MongoDBConnector

# 連線mongodb
mongo_connector = MongoDBConnector()
comment_collection = mongo_connector.get_collection('comment')
drama_collection = mongo_connector.get_collection('drama')
user_collection = mongo_connector.get_collection('user')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = user_collection.find_one({"email": form.email.data})
        if user is not None :
            password = user['password_hash']
            if check_password_hash(password, form.password.data):
                login_user(User(user))
                return redirect(url_for('get_drama'))
        else:
            flash("帳密錯誤，請重新輸入。")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = user_collection.find_one({"email": form.email.data})
        if existing_user:
            flash("該email已經被註冊過了，請使用其他email。")
            return render_template('signup.html', form=form)
        password=form.password.data
        pass_confirm=form.pass_confirm.data
        if password != pass_confirm:
            flash("密碼不符，請重新輸入。")
            return render_template('signup.html', form=form)
        user_dict = {
            "email": form.email.data,
            "username": form.username.data,
            "password_hash": generate_password_hash(form.password.data),
            "create_time": (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        }
        user_collection.insert_one(user_dict)
        new_user = user_collection.find_one({"email": form.email.data})
        login_user(User(new_user))
        # flash("恭喜註冊成為會員，您現在可以收藏喜歡的戲劇。")
        return redirect(url_for('get_drama'))

    return render_template('signup.html', form=form)

@app.route('/member')
@login_required
def member():
    return render_template('member.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.referrer or url_for('get_drama'))
