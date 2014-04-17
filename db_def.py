from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import json

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iovivwytcukmgi:cdigSG1Zx3Ek_ANVRbSAN1r0db@ec2-174-129-197-200.compute-1.amazonaws.com:5432/d660ihttvdl1ls'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False)

    #notes = relationship("Note", order_by="Note.id", backref="account")

    def __init__(self, username):    	
        self.username = username        

    def __repr__(self):
        return '<Account username:%r>' % self.username

    def to_hash(self):
        return {'id': self.id, 'username': self.username}

    def to_json(self):
    	return json.dumps(self.to_hash())


class Context(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40))
    name = db.Column(db.Text())
    description = db.Column(db.Text())    

    def __init__(self, kind, name, description):               
        self.kind = kind
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Context kind:%r, name:%r>' % (self.kind, self.name)

    def to_hash(self):
        return {'id': self.id, 'kind': self.kind, 'name' : self.name, 
            'description' : self.description}            


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40), unique=False)
    content = db.Column(db.Text())
    account_id = db.Column(db.Integer, ForeignKey('account.id'))
    context_id = db.Column(db.Integer, ForeignKey('context.id'))

    account = relationship("Account", backref=backref('notes', order_by=id))
    context = relationship("Context", backref=backref('notes', order_by=id))

    def __init__(self, account_id, context_id, kind, content):       
        self.account_id = account_id
        self.context_id = context_id
        self.kind = kind
        self.content = content

    def __repr__(self):
        return '<Note kind:%r, content:%r>' % (self.kind, self.content)

    def to_hash(self):
        return {'id': self.id, 'kind': self.kind, 'content' : self.content, 
            'medias' : [ x.to_hash() for x in self.medias],
            'context' : self.context.to_hash(),
            'account' : self.account.to_hash()}
    
    def to_json(self):
        return json.dumps(self.to_hash())

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40))
    link = db.Column(db.Text())
    title = db.Column(db.Text())
    note_id = db.Column(db.Integer, ForeignKey('note.id'))

    note = relationship("Note", backref=backref('medias', order_by=id))

    def __init__(self, note_id, kind, title, link):       
        self.note_id = note_id
        self.kind = kind
        self.title = title
        self.link = link

    def __repr__(self):
        return '<Media title:%r>' % self.title

    def get_url(self):
        if self.kind == 'Photo':
            return "https://dl.dropboxusercontent.com/u/5104407/nntest/" + self.link
        else:
            return "http://youtu.be/" + self.link

    def to_hash(self):        
        return {'id' : self.id, 'kind': self.kind, 'title' : self.title, 'link' : self.get_url()}

    def to_json(self):
        return json.dumps(self.to_hash())

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, ForeignKey('account.id'))
    kind = db.Column(db.String(40))
    content = db.Column(db.Text())
    table_name = db.Column(db.String(20))
    row_id = db.Column(db.Integer)

    account = relationship("Account", backref=backref('feedbacks', order_by=id))

    def __init__(self, account_id, kind, content, table_name, row_id):
        self.account_id = account_id
        self.row_id = row_id
        self.table_name = table_name
        self.kind = kind
        self.content = content

    def __repr__(self):
        return '<Feedback by %s: %s on %s: %s >' % (self.account, self.kind, self.table_name, self.content)

    def to_hash(self):        
        return {'kind' : self.kind, 'content': self.content,
            'account': self.account.to_hash(),
            'model': self.table_name}

