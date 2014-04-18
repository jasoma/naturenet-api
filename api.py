import os
from flask import Flask
from flask import request
from flask import Response
from flask import render_template
from flask_bootstrap import Bootstrap
from flask import jsonify

from db_def import db
from db_def import app
from db_def import Account
from db_def import Note
from db_def import Context
from db_def import Media
from db_def import Feedback


import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

cloudinary.config(
  cloud_name = 'university-of-colorado',  
  api_key = '893246586645466',  
  api_secret = '8Liy-YcDCvHZpokYZ8z3cUxCtyk'  
)

import json
import psycopg2

Bootstrap(app)

def success(data):
	return jsonify({"status_code": 200, "status_txt": "OK", 		
		"data": data})

def error(msg):
	return jsonify({"status_code": 400, "status_txt": msg}), 400

@app.route('/api')
def api():
	return "ok"

#
# Account
#

@app.route('/api/accounts/count')
def api_accounts_count():
	n = Account.query.count()
	return jsonify({'success' : True, 'data' : n})

@app.route('/api/account/new/<username>', methods = ['POST','GET'])
def api_account_new(username):
	if request.method == 'POST':
		f = request.form
		if username and 'email' in f and 'name' in f and 'consent' in f and 'password' in f:
			account = Account.query.filter_by(username=username).first()
			if not account:
				newAccount = Account(username)		
				newAccount.name = f['name']
				newAccount.email = f['email']
				newAccount.consent = f['consent']
				newAccount.password = f['password']
				db.session.add(newAccount)
				db.session.commit()
				return success(newAccount.to_hash())		
			return error("Username %s is already taken" % username)
		return error("Username is not specified")
	else:
		return error("the request to add [%s] must be done through a post" % username)

@app.route('/api/account/<username>')
def api_account_get(username):
	account = Account.query.filter_by(username=username).first()
	if account:
		return success(account.to_hash())
	else:
		return error("user does not exist")

@app.route('/api/account/<username>/notes')
def api_account_get_notes(username):
	account = Account.query.filter_by(username=username).first()	
	return success([x.to_hash() for x in account.notes])

@app.route('/api/account/<username>/feedbacks')
def api_account_get_feedbacks(username):
	account = Account.query.filter_by(username=username).first()	
	return success([x.to_hash() for x in account.feedbacks])

@app.route('/api/accounts')
def api_accounts_list():
	accounts = Account.query.all()
	return success([x.to_hash() for x in accounts])

#
# Note
#
@app.route('/api/note/<id>')
def api_note_get(id):
	note = Note.query.get(id)
	return success(note.to_hash())

@app.route('/api/note/<id>/feedbacks')
def api_note_get_feedbacks(id):
	note = Note.query.filter_by(id=id).first()
	feedbacks = Feedback.query.filter_by(table_name='Note', row_id=id).all()
	return success([x.to_hash() for x in feedbacks])


@app.route('/api/note/new/<username>', methods = ['POST', 'GET'])
def api_note_create(username):
	if request.method == 'POST':
		obj = request.form	
		if username and obj and 'content' in obj and 'context' in obj and 'kind' in obj:
			content = obj['content']
			context = obj['context']
			kind = obj['kind']
			a = Account.query.filter_by(username=username).first()
			c = Context.query.filter_by(name=context).first()
			if a and c:
				note = Note(a.id, c.id, kind, content)
				db.session.add(note)
				db.session.commit()
				return success(note.to_hash())
		return error("some parameters are missing")
	else:
		return error("the request must be a post")

#
# Media
#

@app.route('/api/media/<id>')
def api_media_get(id):
	media = Media.query.get(id)
	if media:
		return success(media.to_hash())
	else:
		return error("media object does not exist")

@app.route('/api/media/<id>/feedbacks')
def api_media_get_feedbacks(id):
	feedbacks = Feedback.query.filter_by(table_name='Media', row_id=id).all()
	return success([x.to_hash() for x in feedbacks])

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/api/note/<id>/new/photo', methods = ['POST','GET'])
def api_media_create(id):
	if request.method == 'POST':
		print request.files
		print request.form
		link = ""
		title = request.form["title"] or ""
		kind = "Photo"
		note = Note.query.get(int(id))
		if note:
			media = Media(note.id, kind, title, link) 
			db.session.add(media)
			db.session.commit()
			file = request.files['file']
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				#file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				#print "saving locally to " + filename
				response = cloudinary.uploader.upload(file, public_id = media.id)
				print "uploading to cloudinary .."
				if response:
					print response['url']
					media.link = response['url']
					db.session.add(media)
					db.session.commit()
					return success(media.to_hash())
		return error("note id %d is invalid" % id);
	else:
		return error("adding a media object to note {%s}, this request must be a post." % id)
#
# Context
#
@app.route('/api/context/<id>')
def api_context_get(id):
	context = Context.query.get(id)
	return jsonify({'success': True, 'context' : context.to_hash()})	

@app.route('/api/context/<id>/notes')
def api_context_get_all_notes(id):
	context = Context.query.get(id)
	if context:
		items = context.notes
		return jsonify({'success': True, 
			"notes" : [x.to_hash() for x in items]})


@app.route('/api/context/activities')
def api_context_get_all_activities():
	items = Context.query.filter_by(kind='Activity').all()
	return jsonify({'success': True, 
		"contexts" : [x.to_hash() for x in items]})

@app.route('/api/context/landmarks')
def api_context_get_all_landmarks():
	items = Context.query.filter_by(kind='Landmark').all()
	return jsonify({'success': True, 
		"contexts" : [x.to_hash() for x in items]})



#
# Feedback
#

@app.route('/api/feedback/<id>')
def api_feedback_get(id):
	feedback = Feedback.query.get(id)
	return success(feedback.to_hash())	

@app.route('/api/note/<id>/feedback/<username>/new/comment',
	methods = ['POST', 'GET'])
def api_feedback_add_to_note(id,username):
	if request.method == 'POST':
		note = Note.query.get(id)
		account = Account.query.filter_by(username=username).first()
		if note and account and 'content' in request.form:
			kind = "Comment"
			content = request.form['content']
			table_name = "Note"
			row_id = id
			feedback = Feedback(account.id, kind, content, table_name, row_id)
			db.session.add(feedback)
			db.session.commit()	
			return success(feedback.to_hash())	
		return error("something wrong")
	else:
		return error("add feedback to note [%s] by [%s], this operation must be done through a post" %
			(id, username))

@app.route('/api/media/<id>/feedback/<username>/new/comment',
	methods = ['POST','GET'])
def api_feedback_add_to_media(id,username):
	if request.method == 'POST':
		media = Media.query.get(id)
		account = Account.query.filter_by(username=username).first()
		if media and account and 'content' in request.form:
			kind = "Comment"
			content = request.form['content']
			table_name = "Media"
			row_id = id
			feedback = Feedback(account.id, kind, content, table_name, row_id)
			db.session.add(feedback)
			db.session.commit()	
			return success(feedback.to_hash())	

		return success({'success': False})	
	else:
		return error("add feedback to media [%s] by [%s], this operation must be done through a post" %
			(id, username))


if __name__ == '__main__':
    app.run(debug  = True)