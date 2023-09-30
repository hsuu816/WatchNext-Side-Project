from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('信箱', validators=[DataRequired(), Email()])
    password = PasswordField('密碼',validators=[DataRequired()])
    submit = SubmitField('登入')

class SignupForm(FlaskForm):
    email = StringField('信箱', validators=[DataRequired(), Email()])
    username = StringField('使用者', validators=[DataRequired()])
    password = PasswordField('密碼', validators=[DataRequired()])
    pass_confirm = PasswordField('確認密碼', validators=[DataRequired()])
    submit = SubmitField('註冊')
    