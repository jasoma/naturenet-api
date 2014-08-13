
from trello import TrelloClient
from trello import Board
from trello import List
from trello import Card

import re
from requests_oauthlib import OAuth1

# for MJ
# KEY = 'fcae5554681fa005d12dde8133efdfdd'
# SECRET = '705481ddfca1b757ae1bf431e8fed5b81427d3880ba488cbe9446f848adbabd3'
# TOKEN = '49164242769feef972be6c9a32b94b721cad61ccbb08f0a4fce313af4786c32d'
# for NatureNet Design Team
KEY = '45af258bafe5e40c5798d7c33f55b37f'
SECRET = '512f365abb26ed5c6ac057db6a47aeafae786db981459ce7cf6d8b126db6a49a'
TOKEN = '75a5e2c18b90bb525001b40f2897c35bbad5b7b28b456d0999faa499b6d26ab8'

# CALLBACK_URL_PREFIX = 'http://naturenet-dev.herokuapp.com/api/sync/trello/'
CALLBACK_URL_PREFIX = 'http://naturenet.herokuapp.com/api/sync/trello/'

# naturenet design ideas
# BOARD_ID = 'lm8zPjEG'
BOARD_ID_LONG = '53cddcf33d1a03c9274efe19'
# naturenet-dev
# BOARD_ID = 'WjghHtGP'
# BOARD_ID_LONG = '53d884dd6f7cf5146ff15fbb'

TRELLO_CLIENT = 'NULL'
DEFAULT_LIST = 'To Do'
NEW_OBSERVATIONS_LIST = 'New Observations'

def setup():
    create_client()
    #create_webhooks()

def create_client():
    global TRELLO_CLIENT
    TRELLO_CLIENT = TrelloClient(KEY, SECRET, TOKEN)
    #TRELLO_CLIENT.oath = OAuth1(client_key=KEY, client_secret=SECRET,
    #                            resource_owner_key=TOKEN, verifier=None)
    #TRELLO_CLIENT.oauth.set_verifier(None)


def find_note_id_from_trello_card_desc(desc):
    id = -1
    if not desc:
        return id
    t = re.findall(r"id:\s*\d+", desc)
    if len(t)>0:
        id = t[0].split(':')[1].strip()
    return id

def check_init():
    global TRELLO_CLIENT
    if TRELLO_CLIENT == 'NULL':
        return False
    return True

def create_webhooks():
    global TRELLO_CLIENT
    if not check_init():
        print "Not initialized. Initializing..."
        create_client()
    # remove previous hooks
    hooks = TRELLO_CLIENT.list_hooks(TOKEN)
    for h in hooks:
        h.delete()
    print "existing hooks deleted, now creating hook for board..."
    # creating hook for application
    #TRELLO_CLIENT.create_hook(CALLBACK_URL_PREFIX + KEY, KEY, "SYNC_APP", TOKEN)
    # creating hook for dev board
    TRELLO_CLIENT.create_hook(CALLBACK_URL_PREFIX + BOARD_ID_LONG, BOARD_ID_LONG, "SYNC_BOARD", TOKEN)
    print "re-creating hooks done."

def create_webhook_card(card_id):
    TRELLO_CLIENT.create_hook(CALLBACK_URL_PREFIX + card_id, card_id, "SYNC_CARD_" + card_id, TOKEN)
    print "creating hook for card %s done." % card_id

def get_cards():
    board = Board(TRELLO_CLIENT, BOARD_ID_LONG)
    cards = board.all_cards()
    return cards

def get_card_by_id(id):
    cards = get_cards()
    for c in cards:
        cid = find_note_id_from_trello_card_desc(c.desc)
        if int(cid) == id:
            return c
    return None

def get_list(list_id):
    board = Board(TRELLO_CLIENT, BOARD_ID_LONG)
    list = List(board, list_id)
    return list

def get_list_id(list_name):
    board = Board(TRELLO_CLIENT, BOARD_ID_LONG)
    lists = board.all_lists()
    for x in lists:
        if x.name.lower() == list_name.lower():
            return x.id
    return None

def check_card_existance_in_list(title, list_id):
    list = get_list(list_id)
    cards = list.list_cards()
    for c in cards:
        if c.name == title:
            return c
    return None

def check_card_existance(title):
    cards = get_cards()
    for c in cards:
        if c.name == title:
            return c
    return None

def add_card(title, description, list_name, use_default_list=False):
    if not check_init():
        print "Not initialized. Use setup function to initialize."
        return
    #print "adding card, description %s, length: %s." % (description, len(description))
    if not list_name:
        if use_default_list:
            list_name = DEFAULT_LIST
        else:
            return None
    list_id = get_list_id(list_name)
    if not list_id:
        if use_default_list:
            list_id = get_list_id(DEFAULT_LIST)
            if not list_id:
                return None
        else:
            return None
    if not check_card_existance_in_list(title, list_id):
        list = get_list(list_id)
        c = list.add_card(title, description)
        return c
    return None

def add_card_with_attachment(title, description, list_name, url, use_default_list=False):
    print "the card will have the attachment to url: ", url
    print "title: ", title
    c = add_card(title, description, list_name, use_default_list)
    if not c:
        return None
    print "adding the attachment..."
    c.add_attachment(url, "the attachment")
    return c

def move_card(title, list_name_to):
    if not check_init():
        print "Not initialized. Use setup function to initialize."
        return
    list_id_to = get_list_id(list_name_to)
    c = check_card_existance(title)
    if c:
        c.change_list(list_id_to)
        return c
    return None

def delete_card(title):
    if not check_init():
        print "Not initialized. Use setup function to initialize."
        return
    c = check_card_existance(title)
    if c:
        c.delete()
    return

def update_card(id, title, description):
    if not check_init():
        print "Not initialized. Use setup function to initialize."
        return
    c = get_card_by_id(id)
    print "updating card: title = %s, desc = %s" % (title, description)
    if c:
        c._set_remote_attribute('desc', description)
        c._set_remote_attribute('name', title)
    else:
        print "card not found."
    return

def add_comment_card(id, title, comment_text):
    if not check_init():
        print "Not initialized. Use setup function to initialize."
        return
    c = get_card_by_id(id)
    print "adding comment to card: title = %s" % (title)
    if c:
        c.comment(comment_text)
    return

def comment_exists(card, text):
    card.fetch()
    comments = card.comments
    for comment in comments:
        if comment['data']['text'] == text:
            return True
    return False

