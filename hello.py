import os
from flask import Flask
from flask import request
from flask import render_template

from flask.ext.sqlalchemy import SQLAlchemy

import json
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iovivwytcukmgi:cdigSG1Zx3Ek_ANVRbSAN1r0db@ec2-174-129-197-200.compute-1.amazonaws.com:5432/d660ihttvdl1ls'

db = SQLAlchemy(app)

class User(db.Model):
    uid = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    avatarName = db.Column(db.String(80), unique=False)

    def __init__(self, uid, name, avatarName):
    	self.uid = uid
        self.name = name
        self.avatarName = avatarName

    def __repr__(self):
        return '<User %r>' % self.name

    def to_json(self):
    	return json.dumps({'uid': self.uid, 'name': self.name, 'avatarName': self.avatarName})


class Landmark(db.Model):
	uid = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=False)
	description = db.Column(db.Text, unique=False)
	top = db.Column(db.Integer, unique=False)
	bottom = db.Column(db.Integer, unique=False)
	left = db.Column(db.Integer, unique=False)
	right = db.Column(db.Integer, unique=False)

	def __init__(self, uid):
		self.uid = uid

	def __repr__(self):
		return '<Landmark %r>' % self.__dict__


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/users/list')
def users_json():
	users = User.query.all()
	json_string = json.dumps([{'uid': u.uid, 'name': u.name, 'avatarName': u.avatarName} for u in users])
	return json_string

@app.route('/users/new', methods = ['POST'])
def users_add():
	obj = json.loads(request.data)
	uid = obj['uid']
	name = obj['name']
	avatarName = obj['avatarName']
	if uid and name and avatarName:
		if not User.query.get(long(uid)):
			newUser = User(long(uid), name, avatarName)			
			db.session.add(newUser)
			db.session.commit()
			return newUser.to_json()
		else:
			print "user id [%d] already exists" % long(uid)
			return json.dumps({'success': False})
	else:
		return json.dumps({'success': False})

@app.route('/landmarks/list.json')
def landmarks_json():
	landmarks = Landmark.query.all()
	json_string = json.dumps([{'uid': u.uid, 'name': u.name, "description" : u.description, "top" : u.top, "bottom" : u.bottom, "left" : u.left, "right" : u.right } for u in landmarks])
	return json_string

@app.route('/landmarks/list')
def landmarks():
	landmarks = Landmark.query.all()	
	return render_template('landmarks.html', landmarks=landmarks)

if __name__ == '__main__':
    app.run(debug  = True)
