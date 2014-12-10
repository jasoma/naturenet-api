
from db_def import db
from db_def import WebAccount
from db_def import Note
import trello_api

from datetime import datetime

trello_api.setup()

listname = 'doing'
listid = trello_api.get_list_id(listname)
trello_list = trello_api.get_list(listid)

cards = trello_list.list_cards()

print "number of cards: ", str(len(cards))

for card in cards:
    card.fetch()
    card.fetch_actions()
    actions = card.actions
    for action in actions:
        if action['type'] == 'createCard':
            creator = action['memberCreator']
            account = WebAccount.query.filter_by(username=creator['username']).first()
            if account:
                if not card.desc:
                    note = Note.query.filter_by(content=card.name).first()
                    new_desc = note.to_trello_desc() + "\r\n#likes: 0"
                    card._set_remote_attribute('desc', new_desc)
                else:
                    note_id = trello_api.find_note_id_from_trello_card_desc(card.desc)
                    note = Note.query.get(note_id)
                note.web_username = account.username
                note.trello_card_id = card.id
                note.modified_at = datetime.now()
                db.session.commit()
                print "note_id: %s updated." % (note_id)
                continue
            print "adding webuser: ", creator['username']
            newAccount = WebAccount(creator['username'])
            newAccount.name = creator['fullName']
            newAccount.web_id = creator['id']
            db.session.add(newAccount)
            db.session.commit()
