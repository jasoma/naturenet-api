
import trello_api

trello_api.setup()

listname = 'to do'
listid = trello_api.get_list_id(listname)
trello_list = trello_api.get_list(listid)

cards = trello_list.list_cards()

print "number of cards: ", str(len(cards))

for card in cards:
    card.fetch()
    member_ids = card.idMembers
    print member_ids
