import os
from flask import Flask
from flask import request
from flask import Response
from flask import render_template
from flask import make_response, current_app
from flask_bootstrap import Bootstrap
from flask import jsonify
from flask.json import JSONEncoder

from functools import update_wrapper

from db_def import db
from db_def import app
from db_def import Account
from db_def import Note
from db_def import Context
from db_def import Media
from db_def import Feedback
from db_def import Site

from datetime import datetime
from datetime import timedelta
import calendar

import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

cloudinary.config(
  cloud_name = 'university-of-colorado',  
  api_key = '893246586645466',  
  api_secret = '8Liy-YcDCvHZpokYZ8z3cUxCtyk'  
)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

import json
import psycopg2

Bootstrap(app)

class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                millis = int(
                    calendar.timegm(obj.timetuple()) * 1000 +
                    obj.microsecond / 1000
                )
                return millis
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder  

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
				newAccount.created_at = datetime.now()
				newAccount.icon_url = f.get('icon_url', newAccount.icon_url)
				db.session.add(newAccount)
				db.session.commit()
				return success(newAccount.to_hash())		
			return error("Username %s is already taken" % username)
		return error("Username is not specified")
	else:
		return error("the request to add [%s] must be done through a post" % username)

@app.route('/api/account/<query>')
@crossdomain(origin='*')
def api_account_get(query):
	field = request.args.get("field","username")
	if field == 'username':
		account = Account.query.filter_by(username=query).first()
	else:
		account = Account.query.get(query)
	if account:
		return success(account.to_hash())
	else:
		return error("user does not exist")

@app.route('/api/account/<username>/notes')
@crossdomain(origin='*')
def api_account_get_notes(username):
	account = Account.query.filter_by(username=username).first()	
	return success([x.to_hash() for x in account.notes])

@app.route('/api/account/<username>/feedbacks')
@crossdomain(origin='*')
def api_account_get_feedbacks(username):
	account = Account.query.filter_by(username=username).first()	
	return success([x.to_hash() for x in account.feedbacks])

@app.route('/api/accounts')
@crossdomain(origin='*')
def api_accounts_list():
	accounts = Account.query.all()
	return success([x.to_hash() for x in accounts])

#
# Note
#
@app.route('/api/note/<id>')
@crossdomain(origin='*')
def api_note_get(id):
	note = Note.query.get(id)
	return success(note.to_hash())

@app.route('/api/notes')
@crossdomain(origin='*')
def api_note_list():	
	format = request.args.get('format', 'full')
	n = request.args.get('n',1000)
	notes = Note.query.limit(n)
	return success([x.to_hash(format) for x in notes])

@app.route('/api/note/<id>/feedbacks')
@crossdomain(origin='*')
def api_note_get_feedbacks(id):
	note = Note.query.filter_by(id=id).first()
	feedbacks = Feedback.query.filter_by(table_name='Note', row_id=id).all()
	return success([x.to_hash() for x in feedbacks])

@app.route('/api/note/<id>/update', methods = ['POST'])
def api_note_update(id):
	obj = request.form	
	username = obj.get('username', '')
	account = Account.query.filter_by(username=username).first()
	note = Note.query.get(id)
	if note and account:
		note.content = obj.get('content', note.content)
		note.kind = obj.get('kind', note.kind)
		if 'context' in obj:
			c = Context.query.filter_by(name=obj['context']).first()
			if c == None:
				return error("context %s does not exist" % obj['context'])			
			note.context = c
		note.modified_at = datetime.now()
		db.session.commit()
		return success(note.to_hash())
	return error("some parameters are missing")

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
				if 'longitude' in obj and 'latitude' in obj:
					note.longitude = obj['longitude']
					note.latitude = obj['latitude']
				db.session.add(note)
				db.session.commit()
				return success(note.to_hash())
		return error("some parameters are missing")
	else:
		return error("the request must be a post")

#
# Media
#

@app.route('/api/medias')
def api_media_list():
	medias = Media.query.all()
	return success([x.to_hash() for x in medias])

@app.route('/api/media/<id>')
@crossdomain(origin='*')
def api_media_get(id):
	media = Media.query.get(id)
	if media:
		return success(media.to_hash())
	else:
		return error("media object does not exist")

@app.route('/api/media/<id>/feedbacks')
@crossdomain(origin='*')
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
		print "files: %s" % request.files
		print "form: %s" % request.form
		link = request.form.get("link","")#["link"] or request.form["link"] or ""
		title = request.form.get("title","")#files["title"] or request.form["title"] or ""
		kind = "Photo"
		note = Note.query.get(id)
		print "note: %s" % note
		if note:
			media = Media(note.id, kind, title, link)
			file = request.files.get("file",None)
			print "file: %s" % file
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
		else:
			return error("note id %d is invalid" % id);
	else:
		return error("adding a media object to note {%s}, this request must be a post." % id)
#
# Context
#

@app.route('/api/contexts')
@crossdomain(origin='*')
def api_context_list_all():
	contexts = Context.query.all()
	return success([x.to_hash() for x in contexts])

@app.route('/api/context/<id>')
@crossdomain(origin='*')
def api_context_get(id):
	context = Context.query.get(id)
	return success(context.to_hash())	

@app.route('/api/context/<id>/notes')
@crossdomain(origin='*')
def api_context_get_all_notes(id):
	context = Context.query.get(id)
	if context:
		items = context.notes
		return success([x.to_hash() for x in items])


@app.route('/api/context/activities')
@crossdomain(origin='*')
def api_context_get_all_activities():
	items = Context.query.filter_by(kind='Activity').all()
	return success([x.to_hash() for x in items])

@app.route('/api/context/landmarks')
@crossdomain(origin='*')
def api_context_get_all_landmarks():
	items = Context.query.filter_by(kind='Landmark').all()
	return success([x.to_hash() for x in items])



#
# Feedback
#

@app.route('/api/feedback/<id>')
@crossdomain(origin='*')
def api_feedback_get(id):
	feedback = Feedback.query.get(id)
	return success(feedback.to_hash())	

# def resolve_target(table_name, row_id):
# 	#if table_name in ['Note', 'Context', 'Account']:
# 	if table_name.lower() == 'Note'.lower():
# 		return Note.query.get(row_id)
# 	elif table_name.lower() == 'Context'.lower():
# 		return Context.query.get(row_id)
# 	elif table_name.lower() == 'Accont'.lower():
# 		return Account.query.get(row_id)
# 	elif table_name.lower() == 'Media'.lower():
# 		return Media.query.get(row_id)		
# 	else:
# 		return None

@app.route('/api/feedback/new/<kind>/for/<model>/<id>/by/<username>',
	methods = ['POST', 'GET'])
def api_feedback_add_to_note(kind,model,id,username):
	if request.method == 'POST':
		account = Account.query.filter_by(username=username).first()
		target = Feedback.resolve_target(model,id)
		print "adding feedback [%s] about [%s]" % (kind, target)
		if target and account:
			content = request.form.get('content','')
			table_name = target.__class__.__name__
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



#
# Site
#
@app.route('/api/site/<name>')
@crossdomain(origin='*')
def api_site_get(name):
	site = Site.query.filter_by(name=name).first()	
	if site:
		return success(site.to_hash())
	else:
		return error("site does not exist")

@app.route('/api/site/<name>/long')
@crossdomain(origin='*')
def api_site_get_long(name):
	site = Site.query.filter_by(name=name).first()	
	if site:
		h = site.to_hash()
		h['contexts'] = [c.to_hash() for c in site.contexts]
		return success(h)
	else:
		return error("site does not exist")


@app.route('/api/site/<name>/notes')
@crossdomain(origin='*')
def api_site_get_notes(name):
	site = Site.query.filter_by(name=name).first()
	if site:
		notes = []
		for c in site.contexts:
			notes += c.notes
		return success([x.to_hash() for x in notes])
	else:
		return error("site does not exist")

@app.route('/api/site/<name>/notes/<username>')
@crossdomain(origin='*')
def api_site_get_notes_user(name,username):
	site = Site.query.filter_by(name=name).first()
	account = Account.query.filter_by(username=username).first()
	if site and account:
		all_notes = []
		for c in site.contexts:
			notes = Note.query.filter_by(account_id=account.id, context_id=c.id).all()
			all_notes += notes
		return success([x.to_hash() for x in all_notes])
	else:
		return error("site does not exist")

@app.route('/api/sites')
@crossdomain(origin='*')
def api_site_list():
	sites = Site.query.all()
	return success([x.to_hash() for x in sites])

@app.route('/api/site/<name>/contexts')
@crossdomain(origin='*')
def api_site_list_contexts(name):
	site = Site.query.filter_by(name=name).first()
	if site:
		return success([x.to_hash() for x in site.contexts])
	else:
		return error("site does not exist")

#
# Sync
#
@app.route('/api/sync/accounts/created/since/<year>/<month>/<date>/<hour>/<minute>')
def api_sync_account_since_minute(year,month,date,hour,minute):
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	accounts = Account.query.filter(Account.created_at  >= since_date).all()
	return success([x.to_hash() for x in accounts])

@app.route('/api/sync/accounts/created/since/<year>/<month>/<date>/<hour>/<minute>/at/<site>')
def api_sync_site_account_since_minute(site,year,month,date,hour,minute):	
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	accounts = Account.query.filter(Account.created_at  >= since_date).all()
	site = Site.query.filter_by(name=site).first()
	site_accounts = []
	for a in accounts:
		if any(n.context.site.id == site.id for n in a.notes):
			site_accounts.append(a)
	return success([x.to_hash() for x in site_accounts])

@app.route('/api/sync/notes/created/since/<year>/<month>/<date>/<hour>/<minute>')
def api_sync_notes_since_minute(year,month,date,hour,minute):
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	notes = Note.query.filter(Note.created_at  >= since_date).all()
	return success([x.to_hash() for x in notes])

@app.route('/api/sync/notes/created/since/<year>/<month>/<date>/<hour>/<minute>/at/<site>')
def api_sync_site_notes_since_minute(year,month,date,hour,minute,site):
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	notes = Note.query.filter(Note.created_at  >= since_date).all()
	site = Site.query.filter_by(name=site).first()
	context_ids = [c.id for c in site.contexts]
	notes = [x for x in notes if x.context_id in context_ids]
	return success([x.to_hash() for x in notes])

@app.route('/api/sync/feedbacks/created/since/<year>/<month>/<date>/<hour>/<minute>/at/<site>')
def api_sync_site_feedback_since_minute(site,year,month,date,hour,minute):
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	items = Feedback.query.filter(Feedback.created_at  >= since_date).all()
	site_items = []
	for x in items:
		if x.table_name == 'Note':
			n = Note.query.get(x.row_id)
			if n and n.context.site.name == site:				
				site_items.append(x)
	return success([x.to_hash() for x in site_items])

@app.route('/api/sync/feedbacks/created/since/<year>/<month>/<date>/<hour>/<minute>')
def api_sync_feedback_since_minute(year,month,date,hour,minute):
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	items = Feedback.query.filter(Feedback.created_at  >= since_date).all()
	return success([x.to_hash() for x in items])

@app.route('/api/sync/accounts/created/recent/<n>')
def api_sync_account_recent(n):	
	accounts = Account.query.filter().order_by(Account.created_at.desc()).limit(n)
	return success([x.to_hash() for x in accounts])

@app.route('/api/sync/notes/created/recent/<n>')
def api_sync_note_recent(n):	
	notes = Note.query.filter().order_by(Note.created_at.desc()).limit(n)
	return success([x.to_hash() for x in notes])

if __name__ == '__main__':
    app.run(debug  = True, host='0.0.0.0')