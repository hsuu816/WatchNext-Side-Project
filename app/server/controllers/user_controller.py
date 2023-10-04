from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from server import app, db
from server.models.mysql_user import User
from server.forms.user_forms import LoginForm, SignupForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            # flash("您已經成功的登入")
            return redirect(url_for('get_drama'))
        else:
            flash("帳密錯誤，請重新輸入。")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("該email已經被註冊過了，請使用其他email。")
            return render_template('signup.html', form=form)
        password=form.password.data
        pass_confirm=form.pass_confirm.data
        if password != pass_confirm:
            flash("密碼不符，請重新輸入。")
            return render_template('signup.html', form=form)
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)

        # 存入資料庫
        db.session.add(user)
        db.session.commit()
        login_user(user)
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
