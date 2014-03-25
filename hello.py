import os
from flask import Flask
from flask import request
from flask import Response
from flask import render_template
from flask_bootstrap import Bootstrap


from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

import cloudinary
import cloudinary.api
import cloudinary.uploader

cloudinary.config(
  cloud_name = 'university-of-colorado',  
  api_key = '893246586645466',  
  api_secret = '8Liy-YcDCvHZpokYZ8z3cUxCtyk'  
)

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

    #notes = relationship("Note", order_by="Note.uid", backref="user")

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
	longitude = db.Column(db.Float, unique=False)
	latitude = db.Column(db.Float, unique=False)

	def __init__(self, uid):
		self.uid = uid

	def __repr__(self):
		return '<Landmark %r>' % self.__dict__


class Note(db.Model):
	uid = db.Column(db.BigInteger, primary_key=True)
	comment = db.Column(db.Text, unique=False)
	user_uid = db.Column(db.BigInteger, ForeignKey('user.uid'))
	landmark_uid = db.Column(db.Integer, ForeignKey('landmark.uid'))
	activity_uid = db.Column(db.Integer, ForeignKey('activity.uid'))
	longitude = db.Column(db.String(20), unique=False)
	latitude = db.Column(db.String(20), unique=False)
	categories = db.Column(db.String(80), unique=False)	
	fileId = db.Column(db.String(80))

	landmark = relationship("Landmark")
	user = relationship("User")
	activity = relationship("Activity")

	def __init__(self, uid):
		self.uid = uid

	def __repr__(self):
		return '<Note %r>' % self.__dict__		

	def img_thumbnail(self):
		return cloudinary.CloudinaryImage("%s.jpg" % self.fileId).image(width = 200, height = 200, crop = 'fill')

	def img_large(self):
		return cloudinary.CloudinaryImage("%s.jpg" % self.fileId).image(width = 600, height = 600, crop = 'fit')


class Activity(db.Model):
	uid = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=False)
	description = db.Column(db.Text, unique=False)

	def __init__(self, uid):
		self.uid = uid

	def __repr__(self):
		return '<Activity %r>' % self.__dict__		


#@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/users/<uid>/view')
def user_view(uid):
	user = User.query.get(uid)
	notes = Note.query.filter_by(user_uid=uid).all();
	return render_template('user.html', user=user, notes=notes)

@app.route('/users/list.json')
def users_json():
	users = User.query.all()
	json_string = json.dumps([{'uid': u.uid, 'name': u.name, 'avatarName': u.avatarName} for u in users])
	return json_string

@app.route('/users/list.txt')
def users_list_nn():
	users = User.query.all()
	string = '\n'.join(["{user: id= %d, name= %s, avatarName= %s}" % (u.uid, u.name, u.avatarName) for u in users])
	return Response(string, mimetype='text/plain')

@app.route('/users/list')
def users_list():
	users = User.query.all()
	return render_template('users.html', users=users)	

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

@app.route('/activities/list.json')
def activities_json():
	activities = Activity.query.all()
	json_string = json.dumps([{'uid': u.uid, 'name': u.name, "description" : u.description} for u in activities])
	return json_string

@app.route('/activities/list')
def activities_list():
	activities = Activity.query.all()	
	return render_template('activities.html', activities=activities)

@app.route('/activities/<uid>/view')
def activity_view(uid):
	activity = Activity.query.get(uid)
	notes = Note.query.filter_by(activity_uid=uid).all();
	return render_template('activity.html', activity=activity, notes=notes)

@app.route('/landmarks/list.json')
def landmarks_json():
	landmarks = Landmark.query.all()
	json_string = json.dumps([{'uid': u.uid, 'name': u.name, "description" : u.description, "longitude" : u.longitude, "latitude" : u.latitude} for u in landmarks])
	return json_string

@app.route('/landmarks/list')
def landmarks():
	landmarks = Landmark.query.all()	
	return render_template('landmarks.html', landmarks=landmarks)

@app.route('/landmarks/<uid>/view')
def landmark_view(uid):
	landmark = Landmark.query.get(uid)
	notes = Note.query.filter_by(landmark_uid=uid).all();
	return render_template('landmark.html', landmark=landmark, notes=notes)

@app.route('/notes/list.json')
def notes_json():
	notes = Note.query.all()
	json_string = json.dumps([{'uid': u.uid, "comment" : u.comment,
		"longitude" : u.longitude, "latitude" : u.latitude, "categories" : u.categories, "user_uid" : u.user_uid, 
		"landmark_uid" : u.landmark_uid, "activity_uid" : u.activity_uid, "fileId" : u.fileId
		 } for u in notes])
	return json_string

@app.route('/notes/new', methods = ['POST'])
def notes_new():
	obj = json.loads(request.data)
	uid = obj['uid']

	if not Note.query.get(long(uid)):
		print obj
		newNote = Note(long(uid))		
		newNote.comment = obj['comment']
		newNote.longitude = obj['longitude']
		newNote.latitude = obj['latitude']
		newNote.categories = obj['categories']	
		newNote.user_uid = obj['user_uid']
		newNote.landmark_uid = obj['landmark_uid']
		newNote.activity_uid = obj['activity_uid']
		newNote.fileId = obj['fileId']
		db.session.add(newNote)
		db.session.commit()
		url = "http://drive.google.com/uc?export=view&id=" + note.fileId
  		cloudinary.uploader.upload(url,public_id = note.fileId)
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

@app.route('/notes/<uid>/view')
def notes_view(uid):
	note = Note.query.get(uid)
	return render_template('note.html', note=note)

@app.route('/')
@app.route('/notes/list')
def notes_list():
	notes = Note.query.all()
	return render_template('notes.html', notes=notes)

if __name__ == '__main__':
    app.run(debug  = True)
