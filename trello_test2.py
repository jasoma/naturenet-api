

import trello_api
from db_def import Note
from db_def import Media

print trello_api.KEY

print "Testing: add a card with attachment."

trello_api.create_client()
note = Note.query.get(194)
media = Media.query.filter_by(note_id=194).first()
trello_api.add_card_with_attachment(194, note.content, note.to_trello_desc(), note.status,
                                    media.get_url())

print "Done."
