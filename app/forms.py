from wtforms import StringField, BooleanField, SubmitField, PasswordField
from flask_wtf import FlaskForm
from wtforms.validators import EqualTo, ValidationError, DataRequired
from app.entity import User


class RegisterForm(FlaskForm):
    username = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Password", validators=[DataRequired(), EqualTo("password", "Passwords are not the same")])
    submit = SubmitField("Sing up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Login is taken!")

class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sing in')
