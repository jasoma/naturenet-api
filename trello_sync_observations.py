
import trello_api

from db_def import db
from db_def import Note
from db_def import Media
from db_def import Feedback
from db_def import Site
from db_def import Context
from db_def import Account

from datetime import datetime

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

# medias = Media.query.all()
d1 = datetime(2014, 6, 5)
d2 = datetime(2014, 6, 6)
medias = Media.query.filter(Media.created_at >= d1, Media.created_at < d2).all()
n = 0
print "# of medias", str(len(medias))

for media in medias:
    note = media.note
    if not note:
        continue
    if not note.context:
        continue
    if note.context.id not in context_ids:
        continue
    feedbacks_comment = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==note.id, Feedback.kind=='comment').all()
    feedbacks_like = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==note.id, Feedback.kind=='like').all()
    feedback_landmark = Feedback.query.filter(Feedback.table_name.ilike('note'), Feedback.row_id==note.id, Feedback.kind=='Landmark').first()
    location_text = ""
    if note.kind == "FieldNote" and feedback_landmark:
        location = Context.query.filter_by(name=feedback_landmark.content).first()
        if location:
            location_text = "location: " + location.title + "\r\n"
    new_desc = location_text + note.to_trello_desc() + "\r\n#likes: " + str(len(feedbacks_like))
    card = trello_api.get_card_by_id(note.id)
    new_card = False
    if card:
        # update the card
        card_title = note.content
        if len(card_title) == 0 or media.link == card_title:
            card_title = "[no description]"
        trello_api.update_card(note.id, card_title, new_desc)
    else:
        # create the card
        new_card = True
        n = n + 1
        note.status = str(note.created_at.date())
        db.session.commit()
        if len(note.content) == 0:
            card = trello_api.add_card_with_attachment(note.id, media.link, new_desc, note.status, media.get_url())
        else:
            card = trello_api.add_card_with_attachment(note.id, note.content, new_desc, note.status, media.get_url())
    # updating comments
    for comment in feedbacks_comment:
        account = Account.query.filter_by(id=comment.account_id).first()
        name = 'The Design Team'
        if account:
            name = account.username
        if new_card:
            print "Adding comment to a new card."
            trello_api.add_comment_card(note.id, card.name, "[" + name + "] " + comment.content)
        else:
            e = trello_api.comment_exists(card, comment.content)
            if not e:
                print "Adding comment to an existing card."
                trello_api.add_comment_card(note.id, card.name, "[" + name + "] " + comment.content)

print "Done. (" + str(n) + " cards were added to trello.)"
