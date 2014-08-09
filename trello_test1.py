
import trello_api

print trello_api.KEY

print "creating webhooks"
trello_api.create_webhooks()

# print "executing setup"
# trello_api.setup()
#
# print trello_api.LIST_ID_TO_DO
#
# print "executing add card"
# print trello_api.add_card_to_do("trello_test1.py", "It used oauth1")
#
print "done."
