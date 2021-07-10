from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(150), nullable=False)
    facebook_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website_link=db.Column(db.String(500))
    looking_for_talent = db.Column(db.Boolean, nullable=False, default=False)
    seek_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'artists'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(150), nullable=False)
    facebook_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website_link=db.Column(db.String(500))
    looking_for_venues = db.Column(db.Boolean, nullable=False, default=False)
    seek_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'shows'

    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime)
