#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(120), nullable=False, default='We are looking for an exciting artist to perform here!')
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue Name: {self.name}, City: {self.city}, State: {self.state}>'
    
    @property
    def tuliq_tavsilot(self):
      shows1 = Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == self.id).all()
      shows2 = Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == self.id).all()
     
      return {
        **self.__dict__,
        'shows1': [{
          'artist_id': show1.artist_id,
          'artist_name': show1.artist.name,
          'artist_image_link': show1.artist.image_link,
          'start_time': show1.start_time.strftime("%m/%d/%Y, %H:%M")
          } for show1 in shows1],
        'past_shows_count': len(shows1),
          'shows2': [{
              'artist_id': show2.artist.id,
              'artist_name': show2.artist.name,
              'artist_image_link': show2.artist.image_link,
              'start_time': show2.start_time.strftime("%m/%d/%Y, %H:%M")
          } for show2 in shows2],
        'upcoming_shows_count': len(shows2)
      }


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(120), nullable=False, default='We are looking to perform at an exciting venue!')

    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist Name: {self.name}, City: {self.city}, State: {self.state}>'
    
    @property
    def basic_details(self):
      return { 'id': self.id, 'name': self.name }

    @property
    def tuliq_tavsilot(self):
      shows1 = Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == self.id).all()
      shows2 = Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == self.id).all()

      return {
        **self.__dict__,
        'shows1': [{
          'venue_id': show1.venue_id,
          'venue_name': show1.venue.name,
          'venue_image_link': show1.venue.image_link,
          'start_time': show1.start_time.strftime("%m/%d/%Y, %H:%M")
          } for show1 in shows1],
        'past_shows_count': len(shows1),
        'shows2': [{
            'venue_id': show2.venue.id,
            'venue_name': show2.venue.name,
            'venue_image_link': show2.venue.image_link,
            'start_time': show2.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show2 in shows2],
        'upcoming_shows_count': len(shows2)
}

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))

    @property
    def kutilayotgan(self):
      if self.start_time > datetime.now():
        return {
          "venue_id": self.venue_id,
          "venue_name": Venue.query.get(self.venue_id).name,
          "artist_id": self.artist_id,
          "artist_name": Artist.query.get(self.artist_id).name,
          "artist_image_link": Artist.query.get(self.artist_id).image_link,
          "start_time": self.start_time.strftime("%Y/%m/%d, %H:%M")
        }
      return None

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en_us')

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
  try:
    areas = [{ 'city': V.city, 'state': V.state } for V in Venue.query.distinct(Venue.city, Venue.state).all()] 
    for a in areas:
      a['venues'] = [{'id': V.id, 'name': V.name, 'num_upcoming_shows': V.shows} for V in Venue.query.filter_by(city=a['city']).all()]
    return render_template('pages/venues.html', areas=areas)
  except:
    flash('Xatolik yuz berdi.')
    return redirect(url_for('index'))


@app.route('/venues/search', methods=['POST'])
def search_venues():
  try:
    s1 = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{s1}%')).all()
    response = {
      "count": len(venues),
      "data": [{
        "id": V.id,
        "name": V.name,
        "num_upcoming_shows": len(V.shows)
      } for V in venues]
    }
    return render_template('pages/search_venues.html', results=response, search_term=s1)
  except:
    flash('Xatolik yuz berdi.')
    return redirect(url_for('venues'))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  try:
    data = Venue.query.filter_by(id=venue_id).all()[0]
    return render_template('pages/show_venue.html', venue=data.tuliq_tavsilot)
  except:
    flash('Xatolik yuz berdi.')
    return redirect(url_for('index'))

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    new_venue = Venue(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      address=request.form.get('address'),    
      phone=request.form.get('phone'),
      facebook_link=request.form.get('facebook_link'),
      image_link=request.form.get('image_link'),
      website=request.form.get('website'),
      seeking_talent=request.form.get('seeking_talent') == 'True',
      seeking_description=request.form.get('seeking_description')
    )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An xato occurred. Venue ' + new_venue.name + ' could not be listed.')  
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Successfully deleted venue')
  except:
    flash('An xato occurred when deleting venue, please try again later')
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  try:
    return render_template('pages/artists.html', artists=Artist.query.all())
  except:
    flash('Xatolik yuz berdi')
  return redirect(url_for('index'))

@app.route('/artists/search', methods=['POST'])
def search_artists():
  try:
    s1 = request.form.get('search_term', '')

    artists1 = Artist.query.filter(Artist.name.ilike(f'%{s1}%')).all()

    dict1 = {
      "count": len(artists1),
      "data": [{
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(artist.shows)
      } for artist in artists1]
    }

    return render_template('pages/search_artists.html', results=dict1, search_term=s1)
  except:
    flash('Xatolik yuz berdi.')
  return redirect(url_for('artists'))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  try:
    data = Artist.query.filter_by(id=artist_id).all()[0]
    return render_template('pages/show_artist.html', artist=data.tuliq_tavsilot)
  except:
    print(sys.exc_info())
    flash('Xatolik yuz berdi')
  return redirect(url_for('index'))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).all()[0]
  form = ArtistForm(**artist.__dict__)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.filter_by(id=artist_id).all()[0]
    artist.name=request.form.get('name')
    artist.city=request.form.get('city')
    artist.state=request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.genres=request.form.getlist('genres')
    artist.facebook_link=request.form.get('facebook_link')
    artist.website=request.form.get('website')
    artist.image_link=request.form.get('image_link')
    artist.seeking_venue=request.form.get('seeking_venue') == 'True'
    artist.seeking_description=request.form.get('seeking_description')
    db.session.commit()
  except:
    db.session.rollback()
    flash('Xatolik yuz berdi')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).all()[0]
  form = VenueForm(**venue.__dict__)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.filter_by(id=venue_id).all()[0]
    venue.name=request.form.get('name')
    venue.city=request.form.get('city')
    venue.state=request.form.get('state')
    venue.address=request.form.get('address')
    venue.phone=request.form.get('phone')
    venue.facebook_link=request.form.get('facebook_link')
    venue.website=request.form.get('website')
    venue.image_link=request.form.get('image_link')
    venue.seeking_talent=request.form.get('seeking_talent') == 'True'
    venue.seeking_description=request.form.get('seeking_description')
    db.session.commit()
  except:
    db.session.rollback()
    flash('Xatolik yuz berdi')
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
  try:
    new_artist = Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      genres=request.form.getlist('genres'),
      facebook_link=request.form.get('facebook_link'),
      image_link=request.form.get('image_link'),
      website=request.form.get('website'),
      seeking_venue=request.form.get('seeking_venue') == 'True',
      seeking_description=request.form.get('seeking_description')
    )
 
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An xato occurred. Artist ' + new_artist.name + ' could not be listed.')
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  try:
    data = [s.kutilayotgan for s in Show.query.all() if s.kutilayotgan is not None]
    return render_template('pages/shows.html', shows=data)
  except:
    flash('Xatolik yuz berdi.')
  return redirect(url_for('index'))

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    new_show = Show(
      start_time=request.form.get('start_time'),
      venue_id=request.form.get('venue_id'),
      artist_id=request.form.get('artist_id')
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Xatolik yuz berdi.')
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(xato):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(xato):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('xato.log')
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
