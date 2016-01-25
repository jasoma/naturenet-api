from db_def import db
from db_def import Account
from db_def import Note
from db_def import Media
from db_def import Context

db.drop_all()
db.create_all()

# default = Account("default")
# default.id = 0
# default.password = "0000"
# db.session.add(default)
# db.session.add(Account("tomyeh"))
# db.session.add(Account("abby"))
# db.session.commit()

# testsite = Site("test", "Test Site")
# testsite.id = 0
# db.session.add(site)
# db.session.commit()

# s = Site.query.get(1)

# ask = Context("Activity", "test_ask", "Ask","Find a naturalist and ask a question")
# ask.site = s
# db.session.add(ask)
# find = Context("Activity", "test_find", "Find", "Take a picture of any insect you see today")
# find.site = s
# db.session.add(find)
# db.session.commit()

# c = Context.query.get(1)

# a = Account.query.filter_by(username="tomyeh").first()
# db.session.add(Note(a.id, c.id, "FieldNote", "a note given by tomyeh"))
# db.session.commit()

# n = a.notes[0]
# db.session.add(Media(n.id, "Photo", "first photo taken by tomyeh", "https://dl.dropboxusercontent.com/u/5104407/nntest/bird1.jpg"))
# db.session.add(Media(n.id, "Photo", "second photo taken by tomyeh", "https://dl.dropboxusercontent.com/u/5104407/nntest/bird2.jpg"))
# db.session.add(Media(n.id, "Video", "first video taken by tomyeh", "http://youtu.be/-6eJK9Qu3HY"))
# db.session.commit()


# a = Account.query.filter_by(username="abby").first()
# db.session.add(Note(a.id, c.id, "FieldNote", "a note given by abby"))
# db.session.commit()

# n = a.notes[0]
# db.session.add(Media(n.id, "Photo", "first photo taken by abby", "https://dl.dropboxusercontent.com/u/5104407/nntest/bird3.jpg"))
# db.session.add(Media(n.id, "Photo", "second photo taken by abby", "https://dl.dropboxusercontent.com/u/5104407/nntest/bird4.jpg"))
# db.session.add(Media(n.id, "Video", "first video taken by abby", "http://youtu.be/4ENNzjy8QjU"))
# db.session.commit()

# print n.medias
