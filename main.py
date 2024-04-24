from flask import Flask, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
db = SQLAlchemy(app)
db_math = os.path.join(app.instance_path, 'answers.db')


def create_database():
    conn = sqlite3.connect(db_math)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS answers (description TEXT, answer TEXT)''')
    cursor.execute('SELECT COUNT(*) FROM answers')
    if cursor.fetchone()[0] == 0:
        equations = [
            (
                'Решите уравнение x² − 144 = 0. Если уравнение имеет более одного корня, в ответ запишите меньший из корней.',
                '-12'),
            ('Решите уравнение 10(x − 9) = 7.', '9,7'),
            (
                'Решите уравнение 10x² = 80x. Если уравнение имеет более одного корня, в ответ запишите больший из корней.',
                '8'),
            (
                'Решите уравнение x² − 6x + 5 = 0. Если уравнение имеет более одного корня, в ответ запишите меньший из корней.',
                '1'),
            ('Решите уравнение 9x² = 54x. Если уравнение имеет более одного корня, в ответ запишите больший из корней.',
             '6'),
        ]
        cursor.executemany('INSERT INTO answers VALUES (?, ?)', equations)
        conn.commit()
    conn.close()


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


@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not request.form['surname']:
            request.form['surname'] = user.surname
        if not request.form['name']:
            request.form['name'] = user.name
        user.surname = request.form['surname']
        user.name = request.form['name']
        user.password = request.form['password']
        db.session.commit()
        session['surname'] = user.surname
        session['name'] = user.name
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))


@app.route('/math')
def math():
    return render_template('math.html')


@app.route('/fast-check')
def fast_check():
    return render_template('developing.html')


@app.route('/full-check')
def full_check():
    return render_template('developing.html')


@app.route('/math/equation')
def equations():
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    if not os.path.exists(db_math):
        create_database()
    conn = sqlite3.connect(db_math)
    cursor = conn.cursor()
    cursor.execute("SELECT description, answer FROM answers")
    equations = cursor.fetchall()
    conn.close()
    return render_template('equation.html', equations=equations)


@app.route('/math/inequalities')
def inequalities():
    return render_template('developing.html')


@app.route('/math/function')
def function():
    return render_template('developing.html')


@app.route('/math/planimetry')
def planimetry():
    return render_template('developing.html')


@app.route('/math/stereometry')
def stereometry():
    return render_template('developing.html')


@app.route('/math/vectors')
def vectors():
    return render_template('developing.html')


@app.route('/phys')
def phys():
    return render_template('developing.html')


@app.route('/rus')
def rus():
    return render_template('developing.html')


@app.route('/inf')
def inf():
    return render_template('developing.html')


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
            session['user_id'] = user.id
            session['surname'] = user.surname
            session['name'] = user.name
            return redirect(url_for('home'))
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
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            error = 'Проверьте правильность вводимых данных!'
    return render_template('login.html', form=form, error=error)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
