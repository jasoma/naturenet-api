from openpyxl.reader.excel import load_workbook

from db_def import db
from db_def import Account
from db_def import Note
from db_def import Media
from db_def import Context
from db_def import Feedback

db.drop_all()
db.create_all()


wb = load_workbook(filename = r'data.xlsx')
account_sheet = wb.get_sheet_by_name(name = 'Account')
note_sheet = wb.get_sheet_by_name(name = 'Note')
context_sheet = wb.get_sheet_by_name(name = 'Context')
feedback_sheet = wb.get_sheet_by_name(name = 'Feedback')

n = account_sheet.cell('A1').value
for i in range(2,2+n):
	id = account_sheet.cell('A' + str(i)).value	
	username = account_sheet.cell('B' + str(i)).value
	account = Account(username)
	if id:
		print "create account: %s" % account
		db.session.add(account)
		db.session.commit()

n = context_sheet.cell('A1').value
for i in range(2,2+n):
	id = note_sheet.cell('A' + str(i)).value	
	kind = context_sheet.cell('B' + str(i)).value
	name = context_sheet.cell('C' + str(i)).value
	description = context_sheet.cell('D' + str(i)).value
	context = Context(kind, name, description)

	if id:
		print "create context: %s" % context
		db.session.add(context)
		db.session.commit()


n = note_sheet.cell('A1').value
for i in range(2,2+n):
	id = note_sheet.cell('A' + str(i)).value	
	username = note_sheet.cell('B' + str(i)).value	
	context  = note_sheet.cell('C' + str(i)).value
	kind     = note_sheet.cell('D' + str(i)).value
	content  = note_sheet.cell('E' + str(i)).value	

	media_kind  = note_sheet.cell('F' + str(i)).value	
	media_title = note_sheet.cell('G' + str(i)).value	
	media_url = note_sheet.cell('H' + str(i)).value	

	if id:
		a = Account.query.filter_by(username=username).first()
		c = Context.query.filter_by(name=context).first()
		note = Note(a.id, c.id, kind, content)
		print "create note: %s" % note
		db.session.add(note)
		db.session.commit()
		
		media = Media(note.id, media_kind, media_title, media_url) 
		print "create media: %s" % media
		db.session.add(media)
		db.session.commit()

n = feedback_sheet.cell('A1').value
for i in range(2,2+n):
	table_name = feedback_sheet.cell('B' + str(i)).value	
	row_id  = feedback_sheet.cell('C' + str(i)).value
	kind     = feedback_sheet.cell('D' + str(i)).value
	content  = feedback_sheet.cell('E' + str(i)).value	
	username = feedback_sheet.cell('F' + str(i)).value		

	if id:
		a = Account.query.filter_by(username=username).first()
		feedback = Feedback(a.id, kind, content, table_name, row_id)
		db.session.add(feedback)
		db.session.commit()		
		print "create feedback: %s" % feedback		


#print sheet_ranges.cell('B2').value # D18
