import os
from flask import Flask
from flask import request
from flask import Response
from flask import render_template
from flask_bootstrap import Bootstrap

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

cloudinary.config(
  cloud_name = 'university-of-colorado',  
  api_key = '893246586645466',  
  api_secret = '8Liy-YcDCvHZpokYZ8z3cUxCtyk'  
)

import json
import psycopg2

Bootstrap(app)

@app.route('/api')
def api():
	return "ok"

#
# Account
#

@app.route('/api/accounts/count')
def api_accounts_count():
	n = Account.query.count()
	return json.dumps({'success' : True, 'data' : n})

@app.route('/api/account/new', methods = ['POST'])
def api_account_new():
	obj = json.loads(request.data)
	username = obj['username']
	if username:
		account = Account.query.filter_by(username=username).first()
		if not account:
			newAccount = Account(username)			
			db.session.add(newAccount)
			db.session.commit()
			return json.dumps({'success': True, 'account' : newAccount.to_hash()})	
	
	return json.dumps({'success': False})	

@app.route('/api/account/<username>')
def api_account_get(username):
	account = Account.query.filter_by(username=username).first()
	return json.dumps({'success': True, 'account' : account.to_hash()})	

@app.route('/api/account/<username>/notes')
def api_account_get_notes(username):
	account = Account.query.filter_by(username=username).first()	
	return json.dumps({'success': True, 'notes': [x.to_hash() for x in account.notes]})

@app.route('/api/account/<username>/feedbacks')
def api_account_get_feedbacks(username):
	account = Account.query.filter_by(username=username).first()	
	return json.dumps({'success': True, 'feedbacks': [x.to_hash() for x in account.feedbacks]})

@app.route('/api/accounts')
def api_accounts_list():
	accounts = Account.query.all()
	return json.dumps({'success': True, "accounts": [x.to_hash() for x in accounts]})

#
# Note
#
@app.route('/api/note/<id>')
def api_note_get(id):
	note = Note.query.filter_by(id=id).first()
	return json.dumps({'success': True, "note" : note.to_hash()})

@app.route('/api/note/<id>/feedbacks')
def api_note_get_feedbacks(id):
	note = Note.query.filter_by(id=id).first()
	feedbacks = Feedback.query.filter_by(table_name='Note', row_id=id).all()
	return json.dumps({'success': True, 
		"feedbacks" : [x.to_hash() for x in feedbacks]})


@app.route('/api/note/new', methods = ['POST'])
def api_note_create():
	obj = json.loads(request.data)
	if obj and 'content' in obj and 'context' in obj and 'username' in obj and 'kind' in obj:
		content = obj['content']
		context = obj['context']
		username = obj['username']
		kind = obj['kind']
		a = Account.query.filter_by(username=username).first()
		c = Context.query.filter_by(name=context).first()
		if a and c:
			note = Note(a.id, c.id, kind, content)
			db.session.add(note)
			db.session.commit()
			return json.dumps({'success' : True, 'note' : note.to_hash()})
	return json.dumps({'success': False})	

#
# Media
#

@app.route('/api/media/new', methods = ['POST'])
def api_media_create():
	obj = json.loads(request.data)
	if obj and 'kind' in obj and 'title' in obj and 'note_id' in obj:
		link = "unknown"
		title = obj['title']
		note_id = obj['note_id']
		kind = obj['kind']
		note = Note.query.get(int(note_id))
		if note:
			media = Media(note.id, kind, title, link) 
			db.session.add(media)
			db.session.commit()
			return json.dumps({'success' : True, 'media' : media.to_hash()})
	return json.dumps({'success': False})


@app.route('/api/media/<id>/feedbacks')
def api_media_get_feedbacks(id):
	feedbacks = Feedback.query.filter_by(table_name='Media', row_id=id).all()
	return json.dumps({'success': True, 
		"feedbacks" : [x.to_hash() for x in feedbacks]})


#
# Feedback
#

@app.route('/api/feedback/<id>')
def api_feedback_get(id):
	feedback = Feedback.query.get(id)
	return json.dumps({'success': True, 'feedback' : feedback.to_hash()})	






if __name__ == '__main__':
    app.run(debug  = True)