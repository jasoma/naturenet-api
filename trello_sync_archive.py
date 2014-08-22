
from db_def import db
from db_def import Note
import trello_api

trello_api.setup()

cards = trello_api.get_archived_cards(trello_api.BOARD_ID_LONG_OBSV)
print "number of archived cards: ", str(len(cards))
for c in cards:
    related_note_id = trello_api.find_note_id_from_trello_card_desc(c.desc)
    print "note_id: ", str(related_note_id)
    related_note = Note.query.get(related_note_id)
    if related_note:
        related_note.status = 'deleted'
        db.session.commit()
