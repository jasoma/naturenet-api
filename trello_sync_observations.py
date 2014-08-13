
import trello_api

from db_def import db
from db_def import Note
from db_def import Media
from db_def import Feedback
from db_def import Site
from db_def import Context
from db_def import Account

print "(Server -> Trello) syncing observations..."

trello_api.setup()

site = Site.query.filter(Site.name.ilike('aces')).first()
if not site:
    print "site not found"
    exit(1)

context_ids = []
contexts = Context.query.filter(Context.name.ilike('aces%'), Context.kind.ilike("activity")).all()
if len(contexts) == 0:
    print "no contexts."
    exit(1)

for context in contexts:
    print "adding context: ", context.name
    context_ids.append(context.id)

medias = Media.query.all()
n = 0

for media in medias:
    note = media.note
    if note.context.id not in context_ids:
        continue
    feedbacks_comment = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==note.id, Feedback.kind=='comment').all()
    feedbacks_like = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==note.id, Feedback.kind=='like').all()
    new_desc = note.to_trello_desc() + "\r\n#likes: " + str(len(feedbacks_like))
    card = trello_api.get_card_by_id(note.id)
    new_card = False
    if card:
        # update the card
        trello_api.update_card(note.id, note.content, new_desc)
    else:
        # create the card
        new_card = True
        n = n + 1
        note.status = trello_api.NEW_OBSERVATIONS_LIST
        db.session.commit()
        if len(note.content) == 0:
            card = trello_api.add_card_with_attachment(media.link, new_desc, trello_api.NEW_OBSERVATIONS_LIST, media.get_url())
        else:
            card = trello_api.add_card_with_attachment(note.content, new_desc, trello_api.NEW_OBSERVATIONS_LIST, media.get_url())
    # updating comments
    for comment in feedbacks_comment:
        account = Account.query.filter_by(id=comment.account_id).first()
        name = 'The design team'
        if account:
           name = account.username
        if new_card:
            trello_api.add_comment_card(note.id, card.name, "[" + name + "] " + comment.content)
        else:
            e = trello_api.comment_exists(card, comment.content)
            if not e:
                trello_api.add_comment_card(note.id, card.name, "[" + name + "] " + comment.content)

print "Done. (" + str(n) + " cards were added to trello.)"
