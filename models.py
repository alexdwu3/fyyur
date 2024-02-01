from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from datetime import datetime
db = SQLAlchemy()



# Define the association table for the many-to-many relationship
venue_genres = db.Table('venue_genres',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'))
)
# Define the association table for the many-to-many relationship
artist_genres = db.Table('artist_genres',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'))
)


# Define the Genre model - doing this so it's easier to access genres data even though it's readonly
class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(1000))
    facebook_link = db.Column(db.String(1000))

    # my new fields:
    website_link = db.Column(db.String(1000))  # new field
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    #(DONE) TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venues', lazy=True))
    
    @property
    def upcoming_shows_count(self):
        return len([show for show in self.shows if show.start_time > datetime.now()])

    @property
    def past_shows_count(self):
        return len([show for show in self.shows if show.start_time < datetime.now()])
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer, ForeignKey('Artist.id'))
  start_time = db.Column(db.DateTime, nullable=False)
  image_link = db.Column(db.String(500))
  artist_name = db.Column(db.String(120))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(1000))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(1000))

    # Relationship with Genre model
    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artists', lazy=True))

    # Relationship with Show model
    shows = db.relationship('Show', backref='artist', lazy=True)

    @property
    def upcoming_shows_count(self):
        return len([show for show in self.shows if show.start_time > datetime.now()])

    @property
    def past_shows_count(self):
        return len([show for show in self.shows if show.start_time < datetime.now()])
    #(done) TODO: implement any missing fields, as a database migration using Flask-Migrate

    #(done) TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
