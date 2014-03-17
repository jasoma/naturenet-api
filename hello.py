import os
from flask import Flask
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
import json
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iovivwytcukmgi:cdigSG1Zx3Ek_ANVRbSAN1r0db@ec2-174-129-197-200.compute-1.amazonaws.com:5432/d660ihttvdl1ls'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    avatarName = db.Column(db.String(80), unique=False)

    def __init__(self, id, name, avatarName):
    	self.id = id
        self.name = name
        self.avatarName = avatarName

    def __repr__(self):
        return '<User %r>' % self.name

    def to_json(self):
    	return json.dumps({'id': self.id, 'name': self.name, 'avatarName': self.avatarName})


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/users/list')
def users_json():
	users = User.query.all()
	json_string = json.dumps([{'id': u.id, 'name': u.name, 'avatarName': u.avatarName} for u in users])
	return json_string

@app.route('/users/new', methods = ['POST'])
def users_add():
	obj = json.loads(request.data)
	id = obj['id']
	name = obj['name']
	avatarName = obj['avatarName']
	if id and name and avatarName:
		if not User.query.get(long(id)):
			newUser = User(long(id), name, avatarName)			
			db.session.add(newUser)
			db.session.commit()
			return newUser.to_json()
		else:
			print "user id [%d] already exists" % long(id)
			return json.dumps({'success': False})
	else:
		return json.dumps({'success': False})


if __name__ == '__main__':
    app.run(debug  = True)
