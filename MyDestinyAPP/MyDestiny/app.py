# -*- coding: UTF8 -*-
from flask import Flask, send_file
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
import os
import numpy as np
import SqLiteConnection
import RecommendationSystem as rs
import poi
from constants import *

# App Init
# ----------------------------------------------------------------------------------------- #
# sql = SqLiteConnection(PATH_DB)
app = Flask(__name__)
# TODO Remove debug
app.debug = True

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
app.logger.info('Starting APP MyDestiny')

# Models
# ------------------------------------------------------------------------------------------ #

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
    countries = db.relationship('Country', order_by="Country.name", secondary=countries_users,
                                backref=db.backref('users', lazy='dynamic'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Blueprints
# ----------------------------------------------------------------------------------- #

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile', methods=['GET'])
@login_required
def show_profile():
    countries = Country.query.filter(Country.code.in_(COUNTRY_LIST)).all()
    poi.generate_pois(POI_DEFAULT_CODE)
    # query = "insert into datosmodelo values (125,'{}','',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)".format(current_user.email)
    # sql.execute_query(query)
    map_path = 'poi_map/' + POI_DEFAULT_CODE + '.html'
    return render_template('profile.html', user=current_user, countries_list=countries,
                           map=map_path)


@app.route('/profile/add_country', methods=['POST'])
def add_country_profile():
    # Add country to the user
    c = Country.query.filter_by(id=request.form['countrySelect']).first()
    # query =  "update datosmodelo set {} = 1 where full_name = '{}'".format(c.code,current_user.email)
    if c not in current_user.countries:
        # sql.execute_query(query)
        current_user.countries.append(c)
        db.session.commit()
    return redirect(url_for('show_profile'))


@app.route('/profile/remove_country', methods=['POST'])
def remove_country_profile():
    # Add country to the user
    c = Country.query.filter_by(id=request.form['countrySelect']).first()
    # query =  "update datosmodelo set {} = 0 where full_name = '{}'".format(c.code,current_user.email)
    if c in current_user.countries:
        # sql.execute_query(query)
        current_user.countries.remove(c)
        db.session.commit()
    return redirect(url_for('show_profile'))


@app.route('/profile/suggestion', methods=['POST'])
def suggestion():
    try:
        # Add country to the user
        if current_user.countries:
            # We prepare input for the model
            codes_countries = [c.code for c in current_user.countries]
            # Initalize array with zeros
            array_countries = np.array([0] * 44)
            # Assign ones where the user has traveled
            for code in codes_countries:
                array_countries[COUNTRY_LIST.index(code)] = 1
            list_code_country_result = rs.predict(np.array([array_countries]))
            print str(list_code_country_result)
            code_first = list_code_country_result[0]
            if not os.path.exists(POI_FILE + code_first + '.html'):
                poi.generate_pois(code_first)
            result_country = Country.query.filter_by(code=code_first).first()
            list_result_country = Country.query.filter(Country.code.in_(list_code_country_result[1:])).all()
            result = 'Te recomendamos: ' + result_country.name
        else:
            result = 'Please, add some travel'
    except Exception as e:
        app.logger.error(e)

    countries = Country.query.filter(Country.code.in_(COUNTRY_LIST)).all()
    map_path = '/poi_map/' + code_first + '.html'
    return render_template('profile.html', user=current_user, countries_list=countries, result=result,
                           map=map_path, list_countries=list_result_country)


'''
@app.route('/poi_map')
def show_map_init(code_country=None):
    app.logger.info('Peticion mapa por defecto')
    poi.generate_pois(POI_DEFAULT_CODE)
    app.logger.info('Enviano mapa:' + POI_FILE + POI_DEFAULT_CODE + '.html')
    return send_file(POI_FILE + POI_DEFAULT_CODE + '.html')
'''


@app.route('/poi_map/<map>')
def show_map(map):
    app.logger.info('Peticion mapa: ' + str(map))
    app.logger.info('Enviando mapa:' + POI_FILE + map)
    return send_file(POI_FILE + map)


'''
@app.route('/post_user', methods=['POST'])
def post_user():
    user = User(request.form['username'], request.form['email'])
    print request.form['email']
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))
'''

if __name__ == "__main__":
    app.run()
