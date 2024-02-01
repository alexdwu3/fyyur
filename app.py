#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from sqlalchemy import Boolean, DateTime, func
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

from models import Venue, Artist, Show, Genre

# Initialize Flask-Migrate
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  locations = Venue.query.with_entities(Venue.city, Venue.state).distinct()
  for location in locations:
    # Get all venues in each city/state
    venues = Venue.query.filter_by(state=location.state, city=location.city).all()
    venue_data = []
    for venue in venues:
      # Get the number of upcoming shows for each venue
      num_upcoming_shows = Show.query.join(Venue).filter(
          Show.venue_id == venue.id,
          Show.start_time > datetime.now()
      ).count()
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows,
      })
    data.append({
      "city": location.city,
      "state": location.state,
      "venues": venue_data,
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Get the search term from the form
  search_term = request.form.get('search_term', '')

  # Query the database for venues whose names contain the search term
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  # Prepare the response
  response = {
    "count": len(venues),
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": Show.query.join(Venue).filter(
        Show.venue_id == venue.id,
        Show.start_time > datetime.now()
      ).count(),
    } for venue in venues]
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # Query the database for the venue with the given ID
  venue = Venue.query.get(venue_id)

  if not venue:
    # If no venue with this ID exists, return a 404 error
    abort(404)

  # Query the database for the venue's shows
  past_shows_query = Show.query.filter(Show.venue_id == venue_id, Show.start_time < datetime.now()).all()
  upcoming_shows_query = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.now()).all()

  # Prepare the data for the past shows
  past_shows = [{
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
  } for show in past_shows_query]

  # Prepare the data for the upcoming shows
  upcoming_shows = [{
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
  } for show in upcoming_shows_query]

  # Prepare the data for the venue
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": [genre.name for genre in venue.genres],
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  print(data['website'])
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  print("VENUE IS BEING CREATED YURRRRRRRR")
  form = VenueForm(request.form)
  # (done) TODO: insert form data as a new Venue record in the db, instead
  try:
    venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
    )
    # Handle genres
    genres = Genre.query.filter(func.lower(Genre.name).in_([name.lower() for name in form.genres.data])).all()
    venue.genres = genres

    print("genres", genres)
    
    db.session.add(venue)
    db.session.commit()
    # TODO: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print(str(e))
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  # (done) TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    # Get the venue by id
    venue = Venue.query.get(venue_id)
    if venue:
      # If the venue exists, delete it from the session and commit
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully deleted!')
    else:
      flash('Venue not found.')
  except:
    # If there's an exception, roll back the session and flash an error message
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:
    # Always close the session at the end
    db.session.close()
  return redirect(url_for('index'))
  # (DONE) TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # (done) TODO: replace with real data returned from querying the database
  # Query the database for all artists
  artists = Artist.query.all()

  # Format the data for the template
  data = [{
    "id": artist.id, 
    "name": artist.name, 
    "city": artist.city, 
    "state": artist.state, 
    "phone": artist.phone, 
    "genres": artist.genres,
    "image_link": artist.image_link, 
    "facebook_link": artist.facebook_link, 
    "seeking_venue": artist.seeking_venue, 
    "seeking_description": artist.seeking_description, 
    "upcoming_shows_count": artist.upcoming_shows_count, 
    "past_shows_count": artist.past_shows_count
} for artist in artists]

  print(data)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Get the search term from the form
  search_term = request.form.get('search_term', '')

  # Query the database for artists whose names contain the search term
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  # Prepare the response
  response = {
    "count": len(artists),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len([show for show in artist.shows if show.start_time > datetime.now()]),
    } for artist in artists]
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # Query the database for the artist with the given ID
  artist = Artist.query.get(artist_id)

  if not artist:
    # If no artist with this ID exists, return a 404 error
    abort(404)

  # Query the database for the artist's shows
  past_shows_query = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).all()
  upcoming_shows_query = Show.query.filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).all()

  # Prepare the data for the past shows
  past_shows = [{
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "venue_image_link": show.venue.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
  } for show in past_shows_query]

  # Prepare the data for the upcoming shows
  upcoming_shows = [{
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "venue_image_link": show.venue.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
  } for show in upcoming_shows_query]
  
    # Prepare the data for the artist
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": [genre.name for genre in artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  print(data['website'])
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  print("ARTIST IS BEING CREATED YURRRRRRRR")
  # called upon submitting the new artist listing form
  # (done) TODO: insert form data as a new Artist record in the db, instead
  # (done) TODO: modify data to be the data object returned from db insertion

  try:
  # Create a new Artist object and populate its attributes from the form data
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      seeking_venue=bool(form.seeking_venue.data),
      seeking_description=form.seeking_description.data,
      website_link=form.website_link.data
    )
    genres = Genre.query.filter(func.lower(Genre.name).in_([name.lower() for name in form.genres.data])).all()
    artist.genres = genres

    # Add the new Artist object to the database
    db.session.add(artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally: 
    db.session.close()
  # (done) TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()  # Assuming you have a Show model defined

  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,  # Assuming you have a Venue model with a name attribute
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,  # Assuming you have an Artist model with a name attribute
      "artist_image_link": show.artist.image_link,  # Assuming you have an Artist model with an image_link attribute
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')  # Formatting the start_time as a string
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  print("SHOW IS BEING CREATED YURRRRRRRR")
  # called to create new shows in the db, upon submitting new show listing form

  # Get form data
  form = ShowForm(request.form)
  try: 
    show = Show(
      venue_id=form.venue_id.data,
      artist_id=form.artist_id.data,
      start_time=form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    # On successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # On unsuccessful db insert, flash an error instead.  
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
