
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
from db_def import InteractionLog

import trello_api
import re

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
	return render_template('apis.html')

#
# Account
#

@app.route('/api/accounts/count')
def api_accounts_count():
	n = Account.query.count()
	return jsonify({'success' : True, 'data' : n})

@app.route('/api/account/delete/<username>', methods = ['GET'])
def api_account_delete(username):
	account = Account.query.filter_by(username=username).first()
	if account:
		print "deleting %s " % account.to_hash()
		db.session.delete(account)
		db.session.commit()
		return success({})
	else:
		return error("account does not exist")

@app.route('/api/account/update/<username>', methods = ['POST','GET'])
def api_account_update(username):
    account = Account.query.filter_by(username=username).first()
    if not account:
        return error("User: %s does not exists" % username)
    if request.method == 'POST':
        f = request.form
        if 'email' in f:
            account.email = f['email']
        if 'icon_url' in f:
            account.icon_url = f['icon_url']
        if 'password' in f:
            account.password = f['password']
        if 'consent' in f:
            account.consent = f['consent']
        if 'affiliation' in f:
            account.affiliation = f['affiliation']
        account.modified_at = datetime.now()
        db.session.commit()
        return success(account.to_hash())
    else:
       return error("the request to update [%s] must be done through a post" % username)

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
                if 'icon_url' in f:
                    newAccount.icon_url = f['icon_url']
                else:
                    newAccount.icon_url = f.get('icon_url', newAccount.icon_url)
                if 'affiliation' in f:
                    newAccount.affiliation = f['affiliation']
                else:
                    newAccount.affiliation = ''
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
trello_api.setup()
# print "executing add card"
# print trello_api.add_card_doing("api.py", "It used oauth1 -- test2")

@app.route('/api/note/<id>')
@crossdomain(origin='*')
def api_note_get(id):
	note = Note.query.get(id)
	return success(note.to_hash())

@app.route('/api/note/<id>/delete', methods = ['GET'])
@crossdomain(origin='*')
def api_note_delete(id):
    note = Note.query.get(id)
    if note:
        print "deleting %s " % note.to_hash()
        trello_api.delete_card(note.content)
        db.session.delete(note)
        db.session.commit()
        return success({})
    else:
        return error("note does not exist")

@app.route('/api/notes')
@crossdomain(origin='*')
def api_note_list():	
	format = request.args.get('format', 'full')
	n = request.args.get('n',1000)
	notes = Note.query.limit(n)
	return success([x.to_hash(format) for x in notes])

@app.route('/api/notes/all')
@crossdomain(origin='*')
def api_note_list_all():
	notes = Note.query.all()
	return success([x.to_hash() for x in notes])

@app.route('/api/note/<id>/feedbacks')
@crossdomain(origin='*')
def api_note_get_feedbacks(id):
	note = Note.query.filter_by(id=id).first()
	feedbacks = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id == id).all()
	return success([x.to_hash() for x in feedbacks])

@app.route('/api/note/<id>/update', methods = ['POST'])
def api_note_update(id):
    obj = request.form
    note = Note.query.get(id)
    if note:
        note.content = obj.get('content', note.content)
        note.kind = obj.get('kind', note.kind)
        note.status = obj.get('status', note.status)
        if 'context' in obj:
            c = Context.query.filter_by(name=obj['context']).first()
            if c == None:
                return error("context %s does not exist" % obj['context'])
            note.context = c
        note.modified_at = datetime.now()
        db.session.commit()
        if note.kind == 'DesignIdea':
            feedbacks_comment = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==id, Feedback.kind=='commnet').all()
            feedbacks_like = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==id, Feedback.kind=='like').all()
            new_desc = note.to_trello_desc() + "\r\n#likes: " + str(len(feedbacks_like))# + "\r\n#comments: " + str(len(feedbacks_comment))
            trello_api.update_card(note.content, new_desc)
            trello_api.move_card(note.content, note.status)
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
                if 'status' in obj:
                    note.status = obj['status']
                else:
                    note.status = ''
                db.session.add(note)
                db.session.commit()
                if kind == 'DesignIdea':
                    trello_api.add_card(content, note.to_trello_desc(), note.status)
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
	feedbacks = Feedback.query.filter(Feedback.table_name.ilike('media'), Feedback.row_id==id).all()
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
	items = Context.query.filter(Context.kind.ilike('activity')).all()
	return success([x.to_hash() for x in items])

@app.route('/api/context/landmarks')
@crossdomain(origin='*')
def api_context_get_all_landmarks():
	items = Context.query.filter(Context.kind.ilike('landmark')).all()
	return success([x.to_hash() for x in items])

@app.route('/api/context/<id>/update', methods = ['POST'])
def api_context_update(id):
	obj = request.form
	context = Context.query.get(id)
	if context:
		context.title = obj.get('title', context.title)
		context.description = obj.get('description', context.description)
		context.modified_at = datetime.now()
		db.session.commit()
		return success(context.to_hash())
	return error("some parameters are missing")

@app.route('/api/context/<id>/delete', methods = ['GET'])
def api_context_delete(id):
	# id = request.form.get('id','')
	context = Context.query.get(id)
	if context:
		print "deleting %s " % context.to_hash()
		db.session.delete(context)
		db.session.commit()
		return success({})
	else:
		return error("context does not exist")

@app.route('/api/context/new/activity/at/<site_name>', methods = ['POST'])
def api_context_add_activity(site_name):
    site = Site.query.filter_by(name=site_name).first()
    if not site:
        return error("site does not exists.")
    obj = request.form
    if 'title' in obj and 'description' in obj:
        title = obj['title']
        desc = obj['description']
        new_context = Context("Activity", site.name + "_" + title, title, desc)
        new_context.site_id = site.id
        new_context.site = site
        db.session.add(new_context)
        db.session.commit()
        return success(new_context.to_hash())
    else:
        return error("title or description for the activity not provided.")

#
# Feedback
#

@app.route('/api/feedbacks')
@crossdomain(origin='*')
def api_feedbacks_list_all():
	feedbacks = Feedback.query.all()
	return success([x.to_hash() for x in feedbacks])

@app.route('/api/feedback/<id>')
@crossdomain(origin='*')
def api_feedback_get(id):
	feedback = Feedback.query.get(id)
	return success(feedback.to_hash())	


@app.route('/api/feedback/<id>/update', methods = ['POST'])
def api_feedback_update(id):
	obj = request.form
	username = obj.get('username', '')
	account = Account.query.filter_by(username=username).first()
	feedback = Feedback.query.get(id)
	if feedback and account:
		feedback.content = obj.get('content', feedback.content)
		feedback.kind = obj.get('kind', feedback.kind)
		feedback.modified_at = datetime.now()
		db.session.commit()
		return success(feedback.to_hash())
	return error("some parameters are missing")	

@app.route('/api/feedback/new/<kind>/for/<model>/<id>/by/<username>',
	methods = ['POST', 'GET'])
def api_feedback_add_to_note(kind,model,id,username):
    if request.method == 'POST':
        account = Account.query.filter_by(username=username).first()
        target = Feedback.resolve_target(model,id)
        print "adding feedback [%s] about [%s] by user [%s]" % (kind, target, username)
        if target and account:
            content = request.form.get('content','')
            parent_id = request.form.get('parent_id',0)
            table_name = target.__class__.__name__
            row_id = id
            feedback = Feedback(account.id, kind, content, table_name, row_id, parent_id)
            db.session.add(feedback)
            db.session.commit()
            if model == 'note':
                if target.kind == 'DesignIdea':
                    feedbacks_comment = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==id, Feedback.kind=='comment').all()
                    feedbacks_like = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==id, Feedback.kind=='like').all()
                    trello_api.update_card(target.content, target.to_trello_desc() + "\r\n#likes: " + \
                                       str(len(feedbacks_like)))# + "\r\n#comments: " + str(len(feedbacks_comment)))
                    if kind.lower() == 'comment':
                        account_username = "Anonymous"
                        if account.username != 'default':
                            account_username = account.username
                        trello_api.add_comment_card(target.content, "[" + account_username + "] " + content)
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
			table_name = "media"
			row_id = id
			parent_id = request.form.get('parent_id',0)
			feedback = Feedback(account.id, kind, content, table_name, row_id, parent_id)
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
        ordered_list = []
        for c in site.contexts:
            idx = 0
            if c.title == "Free Observation":
                ordered_list.insert(0,c)
                idx = 1
            else:
                ordered_list.insert(idx,c)
        #print [x.title for x in ordered_list]
        return success([x.to_hash() for x in ordered_list])
    else:
        return error("site does not exist")

#
# Sync
#
@app.route('/api/sync/accounts/created/since/<year>/<month>/<date>/<hour>/<minute>')
def api_sync_account_since_minute(year,month,date,hour,minute):
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	accounts = Account.query.filter(Account.created_at  >= since_date).all()
	return sync_success([x.to_hash() for x in accounts])

@app.route('/api/sync/accounts/created/since/<year>/<month>/<date>/<hour>/<minute>/at/<site>')
def api_sync_site_account_since_minute(site,year,month,date,hour,minute):
    since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
    accounts = Account.query.filter(Account.modified_at  >= since_date).order_by(Account.modified_at.asc()).all()
    the_site = Site.query.filter_by(name=site).first()
    site_accounts = []
    potential_accounts = []
    if not the_site:
        return error("site does not exist")
    for a in accounts:
        if any(n.context.site.id == the_site.id for n in a.notes):
            site_accounts.append(a)
        else:
            potential_accounts.append(a)
    for a in potential_accounts:
        if is_account_related_to_site(a, the_site, True):
            site_accounts.append(a)
    return sync_success([x.to_hash() for x in site_accounts])

@app.route('/api/sync/notes/created/since/<year>/<month>/<date>/<hour>/<minute>')
def api_sync_notes_since_minute(year,month,date,hour,minute):
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	notes = Note.query.filter(Note.created_at  >= since_date).all()
	return sync_success([x.to_hash() for x in notes])

@app.route('/api/sync/notes/created/since/<year>/<month>/<date>/<hour>/<minute>/at/<site>')
def api_sync_site_notes_since_minute(year,month,date,hour,minute,site):
    since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
    notes = Note.query.filter(Note.modified_at  >= since_date).order_by(Note.modified_at.asc()).all()
    the_site = Site.query.filter_by(name=site).first()
    if not the_site:
        return error("site does not exist")
    context_ids = [c.id for c in the_site.contexts]
    notes = [x for x in notes if x.context_id in context_ids]
    return sync_success([x.to_hash() for x in notes])

@app.route('/api/sync/feedbacks/created/since/<year>/<month>/<date>/<hour>/<minute>/at/<site>')
def api_sync_site_feedback_since_minute(site,year,month,date,hour,minute):
    since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
    items = Feedback.query.filter(Feedback.modified_at  >= since_date).order_by(Feedback.modified_at.asc()).all()
    the_site = Site.query.filter_by(name=site).first()
    if not the_site:
        return error("site does not exist")
    site_items = []
    for x in items:
        if x.table_name.lower() == 'note':
            n = Note.query.get(x.row_id)
            if n and n.context.site.name == site:
                site_items.append(x)
        elif x.table_name.lower() == 'context':
            c = Context.query.get(x.row_id)
            if c and c.site.name == site:
                site_items.append(x)
        elif x.table_name.lower() == 'account':
            a = Account.query.get(x.row_id)
            if a and is_account_related_to_site(a, the_site, False):
                site_items.append(x)
    return sync_success([x.to_hash() for x in site_items])

@app.route('/api/sync/feedbacks/created/since/<year>/<month>/<date>/<hour>/<minute>')
def api_sync_feedback_since_minute(year,month,date,hour,minute):
	since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
	items = Feedback.query.filter(Feedback.created_at  >= since_date).all()
	return sync_success(add_timestamp_txt([x.to_hash() for x in items]))


@app.route('/api/sync/interactions/created/since/<year>/<month>/<date>/<hour>/<minute>/at/<site>')
def api_sync_interactions_since_minute(year,month,date,hour,minute,site):
    since_date = datetime(int(year),int(month),int(date),int(hour),int(minute))
    items = InteractionLog.query.filter(InteractionLog.created_at  >= since_date).order_by(InteractionLog.created_at.asc()).all()
    the_site = Site.query.filter_by(name=site).first()
    if not the_site:
        return error("site does not exist")
    site_items = [x for x in items if x.site.id == the_site.id]
    return sync_success(add_timestamp_txt([x.to_hash() for x in site_items]))

@app.route('/api/sync/accounts/created/recent/<n>')
def api_sync_account_recent(n):	
	accounts = Account.query.filter().order_by(Account.created_at.desc()).limit(n)
	return sync_success([x.to_hash() for x in accounts])

@app.route('/api/sync/notes/created/recent/<n>')
def api_sync_note_recent(n):	
	notes = Note.query.filter().order_by(Note.created_at.desc()).limit(n)
	return sync_success([x.to_hash() for x in notes])

@app.route('/api/sync/feedbacks/created/recent/<n>')
def api_sync_feedback_recent(n):	
	feedbacks = Feedback.query.filter().order_by(Feedback.created_at.desc()).limit(n)
	return sync_success([x.to_hash() for x in feedbacks])

@app.route('/api/sync/interactions/created/recent/<n>')
def api_sync_interactions_recent(n):
	interactions = InteractionLog.query.filter().order_by(InteractionLog.created_at.desc()).limit(n)
	return sync_success([x.to_hash() for x in interactions])

#
# Sync with Trello
#
@app.route('/api/sync/trello/<model_id>', methods= ['HEAD', 'POST'])
def api_trello_sync(model_id):
    if model_id != trello_api.BOARD_ID_LONG:
        print "wrong id."
        return error("wrong id.")
    if request.method == 'HEAD':
        print "trello head call."
        return success("hello!")
    if request.method == 'POST':
        d = request.data
        print "trello post call."
        response = json.loads(d)
        action = response['action']
        action_data = action['data']
        card_name = action_data['card']['name']
        print action['type']
        card = trello_api.check_card_existance(card_name)
        if not card:
            print "card not found."
            return error("card not found.")
        account_id_card = 0
        if re.match(r"\[\S+\].+",card_name):
            t_card = re.findall(r"\[\S+\]", card_name)
            account_card = Account.query.filter(Account.username.ilike(t_card[0][1:-1])).first()
            if account_card:
                account_id_card = account_card.id
            card_name = card_name[len(t_card[0]):].lstrip()
        if action['type'] == 'createCard':
            print "a card was created in trello"
            list_name = action_data['list']['name']
            c = Note.query.filter_by(content=card_name).first()
            context_name = 'aces_design_idea'
            context = Context.query.filter_by(name=context_name).first()
            if not c and context:
                note = Note(account_id_card, context.id, 'DesignIdea', card_name)
                note.status = list_name
                db.session.add(note)
                db.session.commit()
            else:
                print "card exists or context does not exists."
                return error("card exists or context does not exists.")
        if action['type'] == 'updateCard':
            print "a card was updated on trello"
            note_id = find_note_id_from_trello_card_desc(card.desc)
            n = Note.query.filter_by(id=note_id).first()
            if not n:
                #c = Note.query.filter_by(content=card_name).first()
                print "cannot find the card in notes."
                return error("cannot find the card in notes.")
            else:
                if 'listAfter' in action_data:
                    list_after = action_data['listAfter']
                    print "the card was moved."
                    n.status = list_after['name']
                    n.modified_at = datetime.now()
                    db.session.commit()
                else:
                    print "looking for update in name field."
                    n.content = card_name
                    n.account_id = account_id_card
                    n.modified_at = datetime.now()
                    db.session.commit()
        if action['type'] == 'commentCard':
            print "a comment was created on trello"
            text = action_data['text']
            account_id = 0
            if re.match(r"\[\S+\].+",text):
                t = re.findall(r"\[\S+\]", text)
                account = Account.query.filter(Account.username.ilike(t[0][1:-1])).first()
                if account:
                    account_id = account.id
                text = text[len(t[0]):].lstrip()
            note_id = find_note_id_from_trello_card_desc(card.desc)
            n = Note.query.filter_by(id=note_id).first()
            if not n:
                print "comment target not found."
                return error("comment target not found.")
            else:
                f = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id == note_id, Feedback.content == text).first()
                if not f:
                    feedback = Feedback(account_id, 'comment', text, 'note', n.id, 0)
                    db.session.add(feedback)
                    db.session.commit()
                else:
                    print "the comment already exists."
                    return error("the comment already exists.")
        if action['type'] == 'updateComment':
            print "a comment was updated on trello"
            old_comment = action_data['old']['text']
            if re.match(r"\[\S+\].+",old_comment):
                t = re.findall(r"\[\S+\]", old_comment)
                old_comment = old_comment[len(t[0]):].lstrip()
            note_id = find_note_id_from_trello_card_desc(card.desc)
            target = Note.query.filter_by(id=note_id).first()
            if target:
                f = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id == note_id, Feedback.content == old_comment).first()
                if f:
                    new_comment = action_data['action']['text']
                    new_comment_account_id = 0
                    if re.match(r"\[\S+\].+",new_comment):
                        t = re.findall(r"\[\S+\]", new_comment)
                        account = Account.query.filter(Account.username.ilike(t[0][1:-1])).first()
                        if account:
                            new_comment_account_id = account.id
                        new_comment = new_comment[len(t[0]):].lstrip()
                    f.content = new_comment
                    f.account_id = new_comment_account_id
                    f.modified_at = datetime.now()
                    db.session.commit()
                else:
                    print "comment not found to update."
                    return error("comment not found to update.")
            else:
                print "target for the comment not found."
                return error("target for the comment not found.")
        return success("thanks!")
    return error("the request must be head or post.")

#
# Interaction Log
#
@app.route('/api/interaction/new/<type>/at/<site>', methods = ['POST','GET'])
def api_interaction_new(type, site):
    if request.method == 'POST':
        f = request.form
        the_site = Site.query.filter_by(name=site).first()
        if not the_site:
            return error("site does not exist")

        if type and 'date' in f and 'touch_x' in f and 'touch_y' in f and 'touch_id' in f and 'details' in f:
            newInteraction = InteractionLog(int(type))
            newInteraction.date = f['date']
            newInteraction.touch_id = f['touch_id']
            newInteraction.touch_x = f['touch_x']
            newInteraction.touch_y = f['touch_y']
            newInteraction.details = f['details']
            newInteraction.site_id = the_site.id
            db.session.add(newInteraction)
            db.session.commit()
            return success(newInteraction.to_hash())
        return error("Interaction type is not specified")
    else:
        return error("the request to add [%s] must be done through a post" % type)

def sync_success(x):
	return success(add_timestamp_txt(x))

def add_timestamp_txt(items):
	for item in items:
		ts = item['created_at']
		item['created_at_debug'] = ts.strftime('%Y/%m/%d/%H/%M')
	return items

def is_account_related_to_site(account, the_site, recursive):
    for f in account.feedbacks:
        if f.kind.lower() == 'comment':
            if f.table_name.lower() == 'Note'.lower():
                note_target = Note.query.get(f.row_id)
                if note_target.context.site.id == the_site.id:
                    return True
            elif f.table_name.lower() == 'Context'.lower():
                context_target = Context.query.get(f.row_id)
                if context_target.site.id == the_site.id:
                    return True
            elif f.table_name.lower() == 'Account'.lower():
                if recursive:
                    account_target = Account.query.get(f.row_id)
                    if is_account_related_to_site(account_target, the_site, False):
                        return True
                continue;
            elif f.table_name.lower() == 'Media'.lower():
                media_target = Media.query.get(f.row_id)
                if media_target.note.context.site.id == the_site.id:
                    return True
            else:
                continue
    return False

def find_note_id_from_trello_card_desc(desc):
    id = -1
    t = re.findall(r"id:\s*\d+", desc)
    if len(t)>0:
        id = t[0].split(':')[1].strip()
    return id

if __name__ == '__main__':
    app.run(debug  = True, host='0.0.0.0')
