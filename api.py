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

@app.route('/api/accounts/count')
def api_accounts_count():
	n = Account.query.count()
	return json.dumps({'success' : True, 'data' : n})

@app.route('/api/account/<username>')
def api_account_get(username):
	account = Account.query.filter_by(username=username).first()
	return account.to_json()

@app.route('/api/account/<username>/notes')
def api_account_get_notes(username):
	account = Account.query.filter_by(username=username).first()	
	return json.dumps({"data": [x.to_hash() for x in account.notes]})

@app.route('/api/accounts')
def api_accounts_list():
	return json.dumps({"data":[{"id" : 10, "username" : "tomyeh"},{"id" : 10, "username" : "abby"}]})

@app.route('/api/note/<id>')
def api_note_get(id):
	note = Note.query.filter_by(id=id).first()
	return note.to_json()


if __name__ == '__main__':
    app.run(debug  = True)