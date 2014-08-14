
import trello_api

print trello_api.KEY

print "creating webhooks"
trello_api.create_webhooks()

# print "executing setup"
# trello_api.setup()
#
print "done."
