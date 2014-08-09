
from db_def import db
from db_def import Site
from db_def import Context

free_obsv1 = Context("Activity", "aces_free_observation", "Free Observation", "")
site = Site.query.filter_by(name='aces').first()
free_obsv1.site_id = site.id
db.session.add(free_obsv1)
db.session.commit()

free_obsv2 = Context("Activity", "uncc_free_observation", "Free Observation", "")
site = Site.query.filter_by(name='uncc').first()
free_obsv2.site_id = site.id
db.session.add(free_obsv2)
db.session.commit()

free_obsv3 = Context("Activity", "umd_free_observation", "Free Observation", "")
site = Site.query.filter_by(name='umd').first()
free_obsv3.site_id = site.id
db.session.add(free_obsv3)
db.session.commit()

