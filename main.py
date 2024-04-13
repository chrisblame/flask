from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])


@app.route('/')
def greetings():
    return render_template('greetings.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    error = None
    if form.validate_on_submit():
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            username=form.username.data,
            password=form.password.data
        )
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            error = 'Пользователь с таким именем уже существует!'
        else:
            db.session.add(user)
            db.session.commit()
            return render_template('home.html')
    return render_template('register.html', form=form, error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data,
            surname=form.surname.data,
            name=form.name.data
        ).first()
        if user and user.password == form.password.data:
            return redirect(url_for('home'))
        else:
            error = 'Проверьте правильность вводимых данных!'
    return render_template('login.html', form=form, error=error)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
