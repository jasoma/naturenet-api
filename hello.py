import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import psycopg2
import urlparse

# urlparse.uses_netloc.append("postgres")
# url = urlparse.urlparse(os.environ["HEROKU_POSTGRESQL_AMBER_URL"])
# print url

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp//test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iovivwytcukmgi:cdigSG1Zx3Ek_ANVRbSAN1r0db@ec2-174-129-197-200.compute-1.amazonaws.com:5432/d660ihttvdl1ls'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    avatarName = db.Column(db.String(80), unique=True)

    def __init__(self, name, avatarName):
        self.name = name
        self.avatarName = avatarName

    def __repr__(self):
        return '<User %r>' % self.name


@app.route('/')
def hello():
    return 'Hello World!'

import json
@app.route('/users.json')
def users_json():
	users = User.query.all()
	json_string = json.dumps([{'id': u.id, 'name': u.name, 'avartarName': u.avatarName} for u in users])
	return json_string


#print json.dumps([{'name': u.name, 'avartarName': u.avatarName} for u in User.query.all()])
# print json.dumps(User.query.all())

if __name__ == '__main__':
    app.run(debug  = True)
