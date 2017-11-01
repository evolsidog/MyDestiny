from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

import os

app = Flask(__name__)
# TODO Remove debug
app.debug = True
# app.config['SEND_REGISTER_EMAIL'] = False

app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
# SQLAlchemy config
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'plaintext'
# Mail config
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'username'
app.config['MAIL_PASSWORD'] = 'password'

db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

countries_users = db.Table('country_users',
                           db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                           db.Column('country_id', db.Integer(), db.ForeignKey('country.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Country(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    code = db.Column(db.String(2))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    countries = db.relationship('Country', secondary=countries_users,
                                backref=db.backref('users', lazy='dynamic'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

'''
# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='vic@gmail.com', password='pass')
    db.session.commit()
'''


@app.route('/')
def index():
    # my_user = User.query.all()
    # one_item = User.query.filter_by(email="ema").first()
    # return render_template('add_user.html', my_user=my_user, one_item=one_item)
    return render_template('index.html')


@app.route('/profile/<email>', methods=['GET'])
@login_required
def show_profile(email):
    user = User.query.filter_by(email=email).first()
    countries = Country.query.all()
    return render_template('profile.html', user=user, countries_list=countries)


@app.route('/profile/add_country', methods=['POST'])
def add_country_profile():
    user = User.query.filter_by(id=request.form['userId']).first()
    # Add country to the user
    c = Country.query.filter_by(id=request.form['countrySelect']).first()
    if c not in user.countries:
        user.countries.append(c)
        db.session.commit()
    countries = Country.query.all()
    return render_template('profile.html', user=user, countries_list=countries)


@app.route('/profile/remove_country', methods=['POST'])
def remove_country_profile():
    user = User.query.filter_by(id=request.form['userId']).first()
    # Add country to the user
    c = Country.query.filter_by(id=request.form['countrySelect']).first()
    if c in user.countries:
        user.countries.remove(c)
        db.session.commit()
    countries = Country.query.all()
    return render_template('profile.html', user=user, countries_list=countries)


@app.route('/profile/suggestion', methods=['POST'])
def suggestion():
    user = User.query.filter_by(id=request.form['userId']).first()
    # Add country to the user
    countries = user.countries
    # TODO Load PKL and return travel
    result = "hola"
    return render_template('profile.html', user=user, countries_list=countries, result=result)


@app.route('/post_user', methods=['POST'])
def post_user():
    user = User(request.form['username'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
