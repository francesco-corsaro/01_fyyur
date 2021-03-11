# Models.
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  #columns with ID
  artist_id = db.Column( db.Integer, db.ForeignKey('artists.id'))
  venue_id = db.Column( db.Integer, db.ForeignKey('venues.id' ))
  # extra data: the date when will be the show
  
  start_time= db.Column( db.DateTime, nullable=False)
  # association
  venue= db.relationship(
      'Venue',
      backref=db.backref('show_venues',  cascade="all, delete"),
      lazy='joined')

  artist= db.relationship(
      'Artist',
      backref=db.backref('show_artists',  cascade="all, delete"),
      lazy='joined')

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # here implement new fields
    genres=db.Column(db.ARRAY(db.String))
    website=db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean, default=False)
    seeking_description=db.Column(db.String(500))
    #relation
    shows = db.relationship('Show', backref=db.backref('venues'), lazy="joined")
    #shows_venue=db.relationship('Show', backref='venues', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):

  __tablename__ = 'artists'
 
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  # here implement new fields
  website=db.Column(db.String(120))
  seeking_venue=db.Column(db.Boolean, default=False)
  seeking_description=db.Column(db.String(500))
  # relation 
  shows = db.relationship('Show', backref=db.backref('artists'), lazy="joined")
    
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
