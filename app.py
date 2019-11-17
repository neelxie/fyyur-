#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_wtf import Form
from forms import *
from models import db, Artist, Show, Venue
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # create empty list to return database results for distinct locations
  data = []
  all_venues = Venue.query.distinct(Venue.city, Venue.state).all()
  # loop through the results appending data to data list
  for venue in all_venues:
    single_venue = {}
    single_venue["venue_city"] = venue.city
    single_venue["venue_state"] = venue.state
    data.append(single_venue)
  
  # loop through each location and getting the venues
  for one_venue in data:
    venues_by_location = Venue.query.filter_by(city=one_venue['venue_city'], state=one_venue['venue_state']).all()
    one_venue["venues"] = [venue for venue in venues_by_location]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.order_by(Venue.id).filter(Venue.name.ilike(f'%{search_term}%'))
  data = [{'name': venue.name, 'id': venue.id} for venue in venues]
  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  past_shows =[]
  upcoming_shows =[]
  past_shows.append(db.session.query(Show).filter_by(venue_id=data.id).filter(Show.start_time < datetime.utcnow().isoformat()).all())
  upcoming_shows.append(db.session.query(Show).filter_by(venue_id=data.id).filter(Show.start_time > datetime.utcnow().isoformat()).all())
  all_past_shows = db.session.query(Show).filter(venue_id == Show.venue_id).filter(Show.start_time < datetime.now()).all()
  all_upcoming_shows = db.session.query(Show).filter(venue_id == Show.venue_id).filter(Show.start_time > datetime.now()).all()

  past_data = []
  upcoming_data = []

  for moja_show in upcoming_shows:
    for anotha in moja_show:
      show_un = {}
      show_un["artist_id"] = anotha.Artist.id
      show_un["artist_name"] = anotha.Artist.name
      show_un["artist_image_link"] = anotha.Artist.image_link
      show_un["start_time"] = anotha.start_time.strftime(("%m/%d/%Y, %H:%M:%S"))
      upcoming_data.append(show_un)
  
  for onne in past_shows:
    for just_one in onne:
      derek_show = {}
      derek_show["artist_id"] = just_one.Artist.id
      derek_show["artist_name"] = just_one.Artist.name
      derek_show["artist_image_link"] = just_one.Artist.image_link
      derek_show["start_time"] = just_one.start_time.strftime(("%m/%d/%Y, %H:%M:%S"))
      past_data.append(derek_show)


  single_venue = {}
  single_venue["id"] = data.id
  single_venue["artist_name"] = data.name
  single_venue["genres"] = data.genres
  single_venue["city"] = data.city
  single_venue["state"] = data.state
  single_venue["phone"] = data.phone
  single_venue["website"] = data.website
  single_venue["facebook_link"] = data.facebook_link
  single_venue["seeking_talent"] = data.seeking_talent
  single_venue["seeking_description"] = data.seeking_description
  single_venue["artist_image_link"] = data.image_link
  single_venue["past_shows_count"] = len(past_shows[0])
  single_venue["past_shows"] = past_data
  single_venue["upcoming_shows"] = upcoming_data
  single_venue["upcoming_shows_count"] = len(upcoming_shows[0])
  
  return render_template('pages/show_venue.html', venue=single_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()

  new_venue = Venue(
    name=request.form.get("name"),
    genres=request.form.get("genres"),
    city=request.form.get("city"),
    state=request.form.get("state"),
    address=request.form.get("address"),
    phone=request.form.get("phone"),
    website=request.form.get("website"),
    image_link=request.form.get("image_link"),
    facebook_link=request.form.get("facebook_link"),
    seeking_talent=request.form.get("seeking_talent"),
    seeking_description=request.form.get("seeking_description")
  )

  db.session.add(new_venue)
  db.session.commit()

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    db.session.close()
    flash('Venue ' + venue_name + ' has been deleted.')
  except Exception as err:
    flash('An error occurred. Venue not deleted.')
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.order_by(Artist.id).filter(Artist.name.ilike(f'%{search_term}%'))
  data = [{'name': artist.name, 'id': artist.id} for artist in artists]
  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  data = Artist.query.get(artist_id)
  past_shows =[]
  upcoming_shows =[]
  past_shows.append(db.session.query(Show).filter_by(artist_id=data.id).filter(Show.start_time < datetime.utcnow().isoformat()).all())
  upcoming_shows.append(db.session.query(Show).filter_by(artist_id=data.id).filter(Show.start_time > datetime.utcnow().isoformat()).all())
  all_past_shows = db.session.query(Show).filter(artist_id == Show.artist_id).filter(Show.start_time < datetime.now()).all()
  all_upcoming_shows = db.session.query(Show).filter(artist_id == Show.artist_id).filter(Show.start_time > datetime.now()).all()

  past_list = []
  upcoming_list = []
  for shows_my in past_shows:
    for nu_show in shows_my:
      upcoming = {}
      upcoming["venue_id"] = nu_show.Venue.id
      upcoming["venue_name"] = nu_show.Venue.name
      upcoming["venue_image_link"] = nu_show.Venue.image_link
      upcoming["start_time"] = nu_show.start_time.strftime(("%m/%d/%Y, %H:%M:%S"))
      upcoming_list.append(upcoming)
  
  for venue_my in upcoming_shows:
    for onne in venue_my:
      past_show = {}
      past_show["venue_id"] = onne.Venue.id
      past_show["venue_name"] = onne.Venue.name
      past_show["venue_image_link"] = onne.Venue.image_link
      past_show["start_time"] = onne.start_time.strftime(("%m/%d/%Y, %H:%M:%S"))
      past_list.append(past_show)

  single_artist = {}
  single_artist["id"] = data.id
  single_artist["artist_name"] = data.name
  single_artist["genres"] = data.genres
  single_artist["city"] = data.city
  single_artist["state"] = data.state
  single_artist["phone"] = data.phone
  single_artist["website"] = data.website
  single_artist["facebook_link"] = data.facebook_link
  single_artist["seeking_venue"] = data.seeking_venue
  single_artist["seeking_description"] = data.seeking_description
  single_artist["artist_image_link"] = data.image_link
  single_artist["past_shows_count"] = len(past_shows[0])
  single_artist["past_shows"] = past_list
  single_artist["upcoming_shows"] = upcoming_list
  single_artist["upcoming_shows_count"] = len(upcoming_shows[0])

  return render_template('pages/show_artist.html', artist=single_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id).__dict__
  form.name.default = artist["name"]
  form.genres.default = artist["genres"]
  form.city.default = artist["city"]
  form.state.default = artist["state"]
  form.phone.default = artist["phone"]
  form.website.default = artist["website"]
  form.image_link.default = artist["image_link"]
  form.facebook_link.default = artist["facebook_link"]
  form.seeking_venue.default = artist["seeking_venue"]
  form.seeking_description.default =  artist["seeking_description"]
  form.process()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  artist = Artist.query.get(artist_id)
  try:
    if artist is not None:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.facebook_link = form.facebook_link.data
      artist.website = form.website
      artist.image_link = form.image_link
      artist.seeking_venue = form.seeking_venue
      artist.seeking_description = form.seeking_description
  
      db.session.commit()
      flash('Artist ' + form.name.data + ' has been updated!')
  except Exception as error:
      flash('Error! Artist' + form.name.data + 'was not updated.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id).__dict__
  form.name.default = venue["name"]
  form.genres.default = venue["genres"]
  form.city.default = venue["city"]
  form.state.default = venue["state"]
  form.phone.default = venue["phone"]
  form.website.default = venue["website"]
  form.image_link.default = venue["image_link"]
  form.facebook_link.default = venue["facebook_link"]
  form.seeking_talent.default = venue["seeking_talent"]
  form.seeking_description.default =  venue["seeking_description"]
  form.process()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)

  try:
    venue = Venue.query.get(venue_id)
    venue.city = form.city.data
    venue.seeking_description = form.seeking_description.data
    venue.seeking_talent = form.seeking_talent.data
    venue.phone = form.phone.data
    venue.state = form.state.data
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website.data
    venue.image_link = form.image_link.data
    venue.address = form.address.data

    db.session.commit()
    flash('Venue has been edited!')
  except:
    flash('Error! Venue was not be edited.')
    db.session.rollback()
  finally:
    db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm()

  new_artist = Artist(
    name=request.form.get("name"),
    genres=request.form.get("genres"),
    city=request.form.get("city"),
    state=request.form.get("state"),
    phone=request.form.get("phone"),
    website=request.form.get("website"),
    image_link=request.form.get("image_link"),
    facebook_link=request.form.get("facebook_link"),
    seeking_venue=request.form.get("seeking_venue"),
    seeking_description=request.form.get("seeking_description")
  )

  db.session.add(new_artist)
  db.session.commit()

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  all_shows = db.session.query(Show).all()
  
  for one_show in all_shows:
    single_show = {}
    single_show["venue_id"] = one_show.id
    single_show["venue_name"] = one_show.Venue.name
    single_show["artist_id"] = one_show.Artist.id
    single_show["artist_name"] = one_show.Artist.name
    single_show["artist_image_link"] = one_show.Artist.image_link
    single_show["start_time"] = one_show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    data.append(single_show)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  artist_id = db.session.query(Artist).filter_by(id = request.form.get("artist_id")).first()
  venue_id = db.session.query(Venue).filter_by(id = request.form.get("venue_id")).first()

  if (artist_id is None) or (venue_id is None):
    flash('Either Artist ID or Venue ID doesnt exist')
  new_show = Show(venue_id=request.form.get("venue_id"), artist_id=request.form.get("artist_id"))
  db.session.add(new_show)
  db.session.commit()


  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
