
from db_def import db
from db_def import WebAccount
import trello_api

trello_api.setup()

listname = 'to do'
listid = trello_api.get_list_id(listname)
trello_list = trello_api.get_list(listid)

cards = trello_list.list_cards()

print "number of cards: ", str(len(cards))

for card in cards:
    card.fetch_actions()
    actions = card.actions
    for action in actions:
        if action['type'] == 'createCard':
            creator = action['memberCreator']
            account = WebAccount.query.filter_by(username=creator['username']).first()
            if account:
                continue
            print "adding webuser: ", creator['username']
            newAccount = WebAccount(creator['username'])
            newAccount.name = creator['fullName']
            newAccount.web_id = creator['id']
            db.session.add(newAccount)
            db.session.commit()
