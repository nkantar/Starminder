from datetime import datetime
import random
import os

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask.ext.github import GitHub
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
import github3
import parsenvy
from waitress import serve


DEPLOYMENT = parsenvy.str('DEPLOYMENT', 'DEVELOPMENT')
PORT = parsenvy.int('PORT', 5000)


app = Flask(__name__)
app.secret_key = str(random.getrandbits(128))

if DEPLOYMENT == 'PRODUCTION':
    DB_URL = parsenvy.str('DATABASE_URL')


elif DEPLOYMENT == 'DEVELOPMENT':
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, 'sm.db')
    DB_URL = 'sqlite:///{0}'.format(full_path)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True)
    github_username = db.Column(db.String(80), unique=True)
    github_token = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    number = db.Column(db.Integer)
    day = db.Column(db.Integer)
    time = db.Column(db.Integer)
    joined = db.Column(db.DateTime)

    def __init__(self, github_id, github_username, github_token, email, number,
                 day, time):
        self.github_id = github_id
        self.github_username = github_username
        self.github_token = github_token
        self.email = email
        self.number = number
        self.day = day
        self.time = time
        self.joined = datetime.now()

    def __repr__(self):
        return '<User {0}>'.format(self.github_username)

    @classmethod
    def create(cls, github_id, github_username, github_token, email='',
               number=10, day=-1, time=0):
        user = User(github_id=github_id,
                    github_username=github_username,
                    github_token=github_token,
                    email=email,
                    number=number,
                    day=day,
                    time=time)
        db.session.add(user)
        db.session.commit()
        return user

    @property
    def as_dict(self):
        return {'id': self.id,
                'github_id': self.github_id,
                'github_username': self.github_username,
                'github_token': self.github_token,
                'email': self.email,
                'number': self.number,
                'day': self.day,
                'time': self.time,
                'joined': self.joined}


db.create_all()


app.config['GITHUB_CLIENT_ID'] = parsenvy.str('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = parsenvy.str('GITHUB_CLIENT_SECRET')
github = GitHub(app)


@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id is not None:
        user = db.session.query(User).filter(User.id == user_id).one()
        session['user'] = user.as_dict

    session['users'] = db.session.query(User).count()

    return render_template('index.html')


@app.route('/save', methods=['POST'])
def save():
    user_id = session['user']['id']
    user = db.session.query(User).filter(User.id == user_id).one()
    user.number = request.form['number']
    user.day = request.form['day']
    user.time = request.form['time']
    user.email = request.form['email']
    db.session.commit()
    flash('Preferences saved! :)')
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete():
    user_id = session['user']['id']
    user = db.session.query(User).filter(User.id == user_id).one()
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash('Account deleted! :(')
    return redirect(url_for('index'))


@app.route('/login')
def login():
    return github.authorize()


@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):

    if oauth_token is not None:
        session['token'] = oauth_token
        gh = github3.login(token=oauth_token)
        gh_user = gh.user()

        user = (db.session.query(User).filter(User.github_id == gh_user.id)
                                      .one_or_none())

        if user is None:
            user = User.create(github_id=gh_user.id,
                               github_username=gh_user.login,
                               github_token=oauth_token,
                               email=gh_user.email)
            flash('Please verify your email address below. :)')

        else:
            user.github_token = oauth_token
            db.session.commit()

        session['user_id'] = user.id

    else:
        flash('Login failed! :(')

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Thank you and come again! :)')
    return redirect(url_for('index'))


if __name__ == '__main__':
    # force SSL only on production
    if DEPLOYMENT == 'PRODUCTION':
        sslify = SSLify(app, subdomains=True, permanent=True)

    waitress_kwargs = {'port': PORT}
    if app.debug:
        waitress_kwargs['host'] = '0.0.0.0'
    serve(app, **waitress_kwargs)
