import os
from flask import Flask
from flask import request
from flask import render_template
from flask_bootstrap import Bootstrap

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

import json
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iovivwytcukmgi:cdigSG1Zx3Ek_ANVRbSAN1r0db@ec2-174-129-197-200.compute-1.amazonaws.com:5432/d660ihttvdl1ls'
Bootstrap(app)

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
	x = db.Column(db.Integer, unique=False)
	y = db.Column(db.Integer, unique=False)

	def __init__(self, uid):
		self.uid = uid

	def __repr__(self):
		return '<Landmark %r>' % self.__dict__


class Note(db.Model):
	uid = db.Column(db.BigInteger, primary_key=True)
	comment = db.Column(db.Text, unique=False)
	user_uid = db.Column(db.BigInteger, ForeignKey('user.uid'))
	landmark_uid = db.Column(db.Integer, ForeignKey('landmark.uid'))
	longitude = db.Column(db.String(20), unique=False)
	latitude = db.Column(db.String(20), unique=False)
	categories = db.Column(db.String(80), unique=False)	
	fileId = db.Column(db.String(80))

	def __init__(self, uid):
		self.uid = uid

	def __repr__(self):
		return '<Note %r>' % self.__dict__		

@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/users/list.json')
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
	json_string = json.dumps([{'uid': u.uid, 'name': u.name, "description" : u.description, "x" : u.x, "y" : u.y} for u in landmarks])
	return json_string

@app.route('/landmarks/list')
def landmarks():
	landmarks = Landmark.query.all()	
	return render_template('landmarks.html', landmarks=landmarks)

@app.route('/notes/list.json')
def notes_json():
	notes = Note.query.all()
	json_string = json.dumps([{'uid': u.uid, "comment" : u.comment,
		"longitude" : u.longitude, "latitude" : u.latitude, "categories" : u.categories, "user_uid" : u.user_uid, 
		"landmark_uid" : u.landmark_uid, "fileId" : u.fileId
		 } for u in notes])
	return json_string

@app.route('/notes/new', methods = ['POST'])
def notes_new():
	obj = json.loads(request.data)
	uid = obj['uid']

	if not Note.query.get(long(uid)):
		newNote = Note(long(uid))		
		newNote.comment = obj['comment']
		newNote.longitude = obj['longitude']
		newNote.latitude = obj['latitude']
		newNote.categories = obj['categories']	
		newNote.user_uid = obj['user_uid']
		newNote.landmark_uid = obj['landmark_uid']
		newNote.fileId = obj['fileId']
		db.session.add(newNote)
		db.session.commit()
		return json.dumps({'success': True})
	else:
		print "user id [%d] already exists" % long(uid)
		return json.dumps({'success': False})

@app.route('/notes/<uid>/update', methods = ['POST'])
def notes_update(uid):
	# obj = json.loads(request.data)
	# obj  = request.args
	obj = request.form

	note = Note.query.get(uid)
	if note:		
		db.session.query(Note).filter_by(uid=uid).update(obj)
		db.session.commit()
		return json.dumps({'success': True})
	else:		
		return json.dumps({'error': "%s is not a valid uid for this note" % uid})		

@app.route('/notes/list')
def notes_list():
	notes = Note.query.all()
	return render_template('notes.html', notes=notes)

if __name__ == '__main__':
    app.run(debug  = True)
