
from db_def import db
from db_def import Site
from db_def import Account
from db_def import Context
from db_def import Note
from db_def import Feedback

from datetime import datetime

import trello_api

trello_api.setup()

site = Site.query.filter(Site.name.ilike('aces')).first()
if not site:
    print "site not found"
    exit(1)

context_name = 'aces_design_idea'
context = Context.query.filter(Context.name.ilike(context_name)).first()

# the commented code will not work, since the comments can have [user] but this code does not consider that

# first pass (trello -> server)
# print "FIRST PASS"
# cards = trello_api.get_cards()
# print "%s cards to sync." % len(cards)
# for c in cards:
#     note_id = trello_api.find_note_id_from_trello_card_desc(c.desc)
#     note = Note.query.get(note_id)
#     new_note = None
#     c.fetch()
#     if not note:
#         print "note not found."
#         # n = Note(0, context.id, 'DesignIdea', c.name)
#         #
#         # list_id = c.idList
#         # #print "list_id: %s" % list_id
#         # board = trello_api.Board(trello_api.TRELLO_CLIENT, trello_api.BOARD_ID_LONG)
#         # #print "board: %s" % board.name
#         # lists = board.all_lists()
#         # for x in lists:
#         #     #print "found list: %s, %s" % (x.id, x.name)
#         #     if x.id == list_id:
#         #         #print "found match, setting the status."
#         #         n.status = x.name
#         # #print "status: %s." % n.status
#         #
#         # db.session.add(n)
#         # db.session.commit()
#         # new_note = n.id
#     # update the comments of the card
#     comments = c.comments
#     for comment in comments:
#         if new_note:
#             print "skipping the card's comments."
#             # feedback = Feedback(0, 'comment', comment['data']['text'], 'note', new_note, 0)
#             # db.session.add(feedback)
#             # db.session.commit()
#         else:
#             f = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==note.id, Feedback.kind=='comment', Feedback.content==comment['data']['text']).first()
#             if not f:
#                 feedback = Feedback(1, 'comment', comment['data']['text'], 'note', note.id, 0)
#                 db.session.add(feedback)
#                 db.session.commit()

# second pass (server -> trello)
# print "SECOND PASS"
ideas = Note.query.filter(Note.kind.ilike('designidea'), Note.context_id==context.id).all()
print "%s ideas to sync." % len(ideas)
num_new_cards = 0
for i in ideas:
    # look if it does not exists in trello create it, else update it
    card = trello_api.get_card_by_id(i.id)
    feedbacks_comment = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==i.id, Feedback.kind=='comment').all()
    feedbacks_like = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==i.id, Feedback.kind=='like').all()
    new_desc = i.to_trello_desc() + "\r\n#likes: " + str(len(feedbacks_like)) + "\r\n#comments: " + str(len(feedbacks_comment))
    new_card = None
    if not card:
        # create it
        num_new_cards = num_new_cards + 1
        if not i.status or i.status == '':
            i.status = trello_api.DEFAULT_LIST
            i.modified_at = datetime.now()
        list_name = i.status
        list_id = trello_api.get_list_id(list_name)
        if not list_id:
            i.status = trello_api.DEFAULT_LIST
            list_name = trello_api.DEFAULT_LIST
        new_card = trello_api.add_card(i.id, i.content, new_desc, list_name, use_default_list=True)
#     # updating the comments
#     for comment in feedbacks_comment:
#         account = Account.query.filter_by(id=comment.account_id).first()
#         name = 'The Design Team'
#         if account:
#            name = account.username
#         if new_card:
#             trello_api.add_comment_card(i.id, new_card.name, "[" + name + "] " + comment.content)
#         else:
#             e = trello_api.comment_exists(card, comment.content)
#             if not e:
#                 trello_api.add_comment_card(i.id, card.name, "[" + name + "] " + comment.content)
# db.session.commit()
print "%s cards created." % num_new_cards
