# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
import logging
from logging import Formatter, FileHandler
from flask_wtf import *
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
import sys
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on
    # number of upcoming shows per venue.

    data = []
    city_state = Venue.query.distinct(Venue.city, Venue.state).all()

    for region in city_state:
        venues_query = Venue.query.filter_by(state=region.state).\
            filter_by(city=region.city).all()
        venue_list = []
        for venue in venues_query:
            show_count = len(Show.query.filter(
                Show.venue_id == venue.id).filter(
                Show.start_time > datetime.now()).all())
            venue_list.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": show_count
            })
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": venue_list
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with
    # partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop"
    # and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    venues_search = Venue.query.filter(
        or_(Venue.state.ilike(f'%{search_term}%'),
            Venue.city.ilike(f'%{search_term}%'),
            Venue.name.ilike(f'%{search_term}%')
            ))
    data = []
    for venue in venues_search:
        show_count = len(Show.query.filter(Show.venue_id == venue.id).filter(
            Show.start_time > datetime.now()).all())
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": show_count
        })
    response = {
        "count": venues_search.count(),
        "data": data
    }

    return render_template('pages/search_venues.html',
                results=response,
                search_term = request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    data = []

    venue_show = Venue.query.filter_by(id=venue_id).all()

    upcoming_shows_count = len(Show.query.filter(
        Show.venue_id == venue_show[0].id).filter(Show.start_time > datetime.now()).all())
    past_shows_count = len(Show.query.filter(Show.venue_id == venue_show[0].id).filter(
        Show.start_time < datetime.now()).all())

    past_shows = []
    past_shows_query = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time). \
        join(Show).filter(and_(Show.venue_id == venue_id),
                          (Show.start_time < datetime.now())).all()

    upcoming_shows = []
    upcoming_shows_query = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time). \
        join(Show).filter(and_(Show.venue_id == venue_id),
                          (Show.start_time > datetime.now())).all()

    for artist in past_shows_query:
        past_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": artist.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    for artist in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": artist.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    data = {
        "id": venue_show[0].id,
        "name": venue_show[0].name,
        "genres": venue_show[0].genres,
        "address": venue_show[0].address,
        "city": venue_show[0].city,
        "state": venue_show[0].state,
        "phone": venue_show[0].phone,
        "website": venue_show[0].website_link,
        "facebook_link": venue_show[0].facebook_link,
        "seeking_talent": venue_show[0].looking_for_talent,
        "seeking_description": venue_show[0].seek_description,
        "image_link": venue_show[0].image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm()
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            looking_for_talent=form.seeking_talent.data,
            seek_description=form.seeking_description.data)
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')


@app.route('/delete/<int:venue_id>', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    venue_to_delete = Venue.query.get(venue_id)
    venue_name = venue_to_delete.name
    print(venue_to_delete)
    try:
        db.session.delete(venue_to_delete)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        # on successful db delete, flash success
        flash('Venue ' + venue_name + ' was successfully deleted!')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    data = []
    artists = Artist.query.all()

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

#   data=[{
#     "id": 4,
#     "name": "Guns N Petals",
#   }, {
#     "id": 5,
#     "name": "Matt Quevedo",
#   }, {
#     "id": 6,
#     "name": "The Wild Sax Band",
#   }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artist_search = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    data = []
    for artist in artist_search:
        show_count = len(Show.query.filter(Show.venue_id == artist.id).filter(
            Show.start_time > datetime.now()).all())
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": show_count
        })
    response = {
        "count": artist_search.count(),
        "data": data
    }

#   response={
#     "count": 1,
#     "data": [{
#       "id": 4,
#       "name": "Guns N Petals",
#       "num_upcoming_shows": 0,
#     }]
#   }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    data = []

    artist_show = Artist.query.filter_by(id=artist_id).all()

    upcoming_shows_count = len(Show.query.filter(
        Show.artist_id == artist_show[0].id).filter(Show.start_time > datetime.now()).all())
    past_shows_count = len(Show.query.filter(Show.artist_id == artist_show[0].id).filter(
        Show.start_time < datetime.now()).all())

    past_shows = []
    past_shows_query = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time). \
        join(Show).filter(and_(Show.artist_id == artist_id),
                          (Show.start_time < datetime.now())).all()

    upcoming_shows = []
    upcoming_shows_query = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time). \
        join(Show).filter(and_(Show.artist_id == artist_id),
                          (Show.start_time > datetime.now())).all()

    for venue in past_shows_query:
        past_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": venue.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    for venue in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": venue.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    data = {
        "id": artist_show[0].id,
        "name": artist_show[0].name,
        "genres": artist_show[0].genres,
        "city": artist_show[0].city,
        "state": artist_show[0].state,
        "phone": artist_show[0].phone,
        "website": artist_show[0].website_link,
        "facebook_link": artist_show[0].facebook_link,
        "seeking_venue": artist_show[0].looking_for_venues,
        "seeking_description": artist_show[0].seek_description,
        "image_link": artist_show[0].image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_edit_query = Artist.query.get(artist_id)

    form.name.data = artist_edit_query.name
    form.genres.data = artist_edit_query.genres
    form.city.data = artist_edit_query.city
    form.state.data = artist_edit_query.state
    form.phone.data = artist_edit_query.phone
    form.website_link.data = artist_edit_query.website_link
    form.facebook_link.data = artist_edit_query.facebook_link
    form.seeking_venue.data = artist_edit_query.looking_for_venues
    form.seeking_description.data = artist_edit_query.seek_description
    form.image_link.data = artist_edit_query.image_link

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist_edit_query)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    try:
        artist = {
            "name": form.name.data,
            "city": form.city.data,
            "state": form.state.data,
            "phone": form.phone.data,
            "genres": form.genres.data,
            "facebook_link": form.facebook_link.data,
            "image_link": form.image_link.data,
            "website_link": form.website_link.data,
            "looking_for_venues": form.seeking_venue.data,
            "seek_description": form.seeking_description.data}
        db.session.query(Artist).filter(Artist.id == artist_id).\
            update(artist, synchronize_session="fetch")
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    form = VenueForm()
    venue_edit_query = Venue.query.get(venue_id)

    form.name.data = venue_edit_query.name
    form.city.data = venue_edit_query.city
    form.state.data = venue_edit_query.state
    form.address.data = venue_edit_query.address
    form.phone.data = venue_edit_query.phone
    form.genres.data = venue_edit_query.genres
    form.facebook_link.data = venue_edit_query.facebook_link
    form.image_link.data = venue_edit_query.image_link
    form.website_link.data = venue_edit_query.website_link
    form.seeking_talent.data = venue_edit_query.looking_for_talent
    form.seeking_description.data = venue_edit_query.seek_description

    return render_template('forms/edit_venue.html', form=form, venue=venue_edit_query)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    try:
        venue = {
            "name": form.name.data,
            "city": form.city.data,
            "state": form.state.data,
            "address": form.address.data,
            "phone": form.phone.data,
            "genres": form.genres.data,
            "facebook_link": form.facebook_link.data,
            "image_link": form.image_link.data,
            "website_link": form.website_link.data,
            "looking_for_talent": form.seeking_talent.data,
            "seek_description": form.seeking_description.data}
        db.session.query(Venue).filter(Venue.id == venue_id).\
            update(venue, synchronize_session="fetch")
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm()
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            looking_for_venues=form.seeking_venue.data,
            seek_description=form.seeking_description.data)
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return render_template('pages/home.html')


@app.route('/artists/delete/<int:artist_id>', methods=['GET'])
def delete_artist(artist_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    artist_to_delete = Artist.query.get(artist_id)
    artist_name = artist_to_delete.name
    print(artist_to_delete)
    try:
        db.session.delete(artist_to_delete)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        # on successful db delete, flash success
        flash('Artist ' + artist_name + ' was successfully deleted!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    all_shows_query = db.session.query(Show).\
        join(Artist, Show.artist_id == Artist.id).\
        join(Venue, Show.artist_id == Venue.id).all()
    data = []
    for all_shows in all_shows_query:
        data.append({
            "venue_id": all_shows.venue.id,
            "venue_name": all_shows.venue.name,
            "artist_id": all_shows.artist.id,
            "artist_name": all_shows.artist.name,
            "artist_image_link": all_shows.artist.image_link,
            "start_time": all_shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form[' do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm()
    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
