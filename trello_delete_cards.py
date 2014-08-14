

import trello_api

# list_name = "New Observations"
list_name = "2014-06-06"

trello_api.setup()
trello_api.delete_cards(list_name)

# trello_api.delete_all_cards()
