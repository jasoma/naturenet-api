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

    def to_json(self):
    	return json.dumps({'id': self.id, 'username': self.username})


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40), unique=False)
    content = db.Column(db.Text())
    account_id = db.Column(db.Integer, ForeignKey('account.id'))

    account = relationship("Account", backref=backref('notes', order_by=id))

    def __init__(self, account_id, kind, content):       
        self.account_id = account_id
        self.kind = kind
        self.content = content

    def __repr__(self):
        return '<Note %r>' % self.__dict__ 

    def to_hash(self):
        return {'id': self.id, 'kind': self.kind, 'content' : self.content, 
            'media' : [ x.to_hash() for x in self.medias]}
    
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

    def to_hash(self):        
        return {'id' : self.id, 'kind': self.kind, 'title' : self.title, 'link' : self.link}

