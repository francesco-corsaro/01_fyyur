#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for,
  jsonify, 
  abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys 
from flask_migrate import Migrate
import datetime

# here import my models 
from models import db, Venue, Artist, Show 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# configuration of db with mexternal models
db.init_app(app)

# TODO: connect to a local postgresql database
migrate= Migrate(app,db)
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  """
  data=[]

  # db query
  all_venues=Venue.query
  all_shows=Show.query

  cities=list(dict.fromkeys([x.city for x in all_venues]))

  cities.sort()

  for city in cities :
    
    venues_obj={
      "city": city
    }
    place=[]
    
    infoS=all_venues.filter(Venue.city==city).order_by(Venue.name)

    for info in infoS:
      venues_obj['state']= info.state

      info_venue={
        'id':info.id,
        'name':info.name
      }
      
      upcoming_shows=all_shows.\
        filter(Show.venue_id==info.id).\
        filter(Show.start_time >= datetime.datetime.now())

      info_venue['num_upcoming_shows']= upcoming_shows.count()

      place.append(info_venue)
    
    venues_obj['venues']= place
    data.append(venues_obj)"""

  locals = []
  venues = Venue.query.all()

  places = Venue.query.distinct(Venue.city, Venue.state).all()

  for place in places:
      locals.append({
          'city': place.city,
          'state': place.state,
          'venues': [{
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.datetime.now()])
          } for venue in venues if
              venue.city == place.city and venue.state == place.state]
      })
  return render_template('pages/venues.html', areas=locals)
  #return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data=[]
  search_term=request.form.get('search_term', '')

  corrispondences= Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term )))
  for corrispondence in corrispondences:
    my_obj= {
      'id':corrispondence.id,
      'name':corrispondence.name
    }
    upcoming_shows=Show.query.filter(Show.venue_id == corrispondence.id )
    my_obj['num_upcoming_shows']=upcoming_shows.count()
    data.append(my_obj)
  
  response={
    "count": corrispondences.count(),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # prima seleziono la tabella Venues e poi 
  # e poi seleziono una query con inner join Show e Artist 
  # faccio un cilco 
  # per dividerli in base alla data  in past and up coming
  # e metto una variabile per contarli

  # here we get values of Venue by ID
  data_venue=Venue.query.filter(Venue.id==venue_id).first()
  
  result={
    "id": data_venue.id ,
    "name": data_venue.name,
    "genres": data_venue.genres,
    "address": data_venue.address ,
    "city": data_venue.city,
    "state": data_venue.state ,
    "phone": data_venue.phone,
    "website": data_venue.website,
    "facebook_link": data_venue.facebook_link,
    "seeking_talent": data_venue.seeking_talent,
    "seeking_description": data_venue.seeking_description,
    "image_link":data_venue.image_link
  }

  # we get values of show with artisti
  data_show= db.session.query(Show.artist_id, Show.start_time, Artist.id, Artist.name, Artist.image_link).join(Artist).filter(Show.venue_id==venue_id).all()
  past_shows=[]
  past_shows_count=0
  upcoming_shows=[]
  upcoming_shows_count=0
  
  # we assign values for the past and upcoming show
  for row in data_show:
    
    show_event={
      "artist_id":row.artist_id,
      "artist_name":row.name,
      "artist_image_link":row.image_link,
      "start_time":row.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if row.start_time < datetime.datetime.now():
      past_shows_count+=1
      past_shows.append(show_event )
    else:
      upcoming_shows_count+=1
      upcoming_shows.append(show_event)

  # append the values to object to send
  result["past_shows"]=past_shows
  result["upcoming_shows"]=upcoming_shows
  result["past_shows_count"]=past_shows_count
  result["upcoming_shows_count"]=upcoming_shows_count

  return render_template('pages/show_venue.html', venue=result)

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
  form = VenueForm(request.form, meta={'csrf': False})

  if form.validate():
    error=False
    try:
      # form = VenueForm() // Moved out
      name=form.name.data
      new_row = Venue(
        name=name,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website=form.website.data,
        seeking_talent= True if form.seeking_talent.data == 'True' else False,
        seeking_description=form.seeking_description.data
      )
      
      db.session.add(new_row)
      db.session.commit()
    except:
       # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + new_row.name + ' could not be listed.')
    finally:
      db.session.close()
    if error:
      abort(400)
    else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    # keep in the same page 
    return redirect( url_for('create_venue_form') )
   
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue_delete=Venue.query.get(venue_id)
    db.session.delete(venue_delete)
    db.session.commit()
    flash(' Venue ' + venue_delete.name + '  deleted.')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venue_delete.name + ' could not be deleted.')
  finally:
    db.session.close()
    
  return render_template('pages/home.html')
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=db.session.query(Artist.id, Artist.name).order_by(Artist.name).all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data=[]
  search_term=request.form.get('search_term', '')
  
  # artist_searched select Artists  
  artist_searched= Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term )))
  # shows_searched select the show filtered by Artist.name and the date of Show.start_time
  shows_searched=db.session.\
    query(Artist.name, Artist.id, Show.start_time, Show.artist_id).\
    join(Artist).\
    filter(Artist.name.ilike('%{}%'.format(search_term ))).\
    filter(Show.start_time >= datetime.datetime.now())

  for row in artist_searched:
    myObj={
      'id':row.id,
      'name':row.name,
      'num_upcoming_shows': shows_searched.filter(Show.artist_id == row.id).count(),
    }
    data.append(myObj)

  response={
    "count": artist_searched.count(),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  data_artist= Artist.query.get(artist_id)

  data={
    "id": data_artist.id ,
    "name": data_artist.name,
    "genres": data_artist.genres,
    "city": data_artist.city,
    "state": data_artist.state ,
    "phone": data_artist.phone,
    "website": data_artist.website,
    "facebook_link": data_artist.facebook_link,
    "seeking_venue": data_artist.seeking_venue,
    "seeking_description": data_artist.seeking_description,
    "image_link":data_artist.image_link
  }

  artist_shows=db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time, Show.artist_id ,Show.venue_id).join(Venue).filter(Show.artist_id==artist_id).all()

  past_shows=[]
  past_shows_count=0
  upcoming_shows=[]
  upcoming_shows_count=0

  for row in artist_shows:
    show_event={
      "venue_id":row.venue_id,
      "venue_name":row.name,
      "venue_image_link":row.image_link,
      "start_time":row.start_time.strftime("%m/%d/%Y, %H:%M"),
    }
    if row.start_time < datetime.datetime.now():
      past_shows_count+=1
      past_shows.append(show_event )
    else:
      upcoming_shows_count+=1
      upcoming_shows.append(show_event)
  
  data["past_shows"]=past_shows
  data["upcoming_shows"]=upcoming_shows
  data["past_shows_count"]=past_shows_count
  data["upcoming_shows_count"]=upcoming_shows_count

  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form=ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    error=False
    try:
      #form = ArtistForm()
      
      new_row = Artist.query.get(artist_id)
      new_row.name=form.name.data
      new_row.city=form.city.data
      new_row.state=form.state.data
      
      new_row.phone=form.phone.data
      if form.genres.data :
        new_row.genres=form.genres.data
      new_row.facebook_link=form.facebook_link.data
      new_row.image_link=form.image_link.data
      new_row.website=form.website.data
      if form.seeking_venue.data:
        if form.seeking_venue.data == 'True':
          new_row.seeking_venue=True
        else:
          new_row.seeking_venue=False
        new_row.seeking_description=form.seeking_description.data
    
      db.session.commit()
    except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + new_row.name + ' could not be edited.')
    finally:
      db.session.close()
    if error:
      abort(400)
    else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    
    error=False
    try:
      
      
      new_row = Venue.query.get(venue_id)
      new_row.name=form.name.data
      new_row.city=form.city.data
      new_row.state=form.state.data
      new_row.address=form.address.data
      new_row.phone=form.phone.data
      if form.genres.data :
        new_row.genres=form.genres.data
      new_row.facebook_link=form.facebook_link.data
      new_row.image_link=form.image_link.data
      new_row.website=form.website.data
      if form.seeking_talent.data:
        
        if form.seeking_talent.data == 'True':
          new_row.seeking_talent=True
        else:
          new_row.seeking_talent=False
        new_row.seeking_description=form.seeking_description.data
    
      db.session.commit()
    except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + new_row.name + ' could not be edited.')
    finally:
      db.session.close()
    if error:
      abort(400)
    else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

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
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    error=False
    try:

      form = ArtistForm()

      name=form.name.data
      
      new_row = Artist(
        name=name,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website=form.website.data,
        seeking_venue=True if form.seeking_venue.data =='True' else False,
        seeking_description=form.seeking_description.data
      )
      print(type(form.seeking_venue.data))

      db.session.add(new_row)
      db.session.commit()
    except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + new_row.name + ' could not be listed.')
    finally:
      db.session.close()
    if error:
      abort(400)
    else:
        # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    # keep in the same page 
    return redirect( url_for('create_artist_form') )
    
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  event_query=db.session.\
    query(Show.venue_id, Venue.name, Show.artist_id, Artist.name.label('artist_name'), Artist.image_link, Show.start_time).\
    join(Venue, Show.venue_id== Venue.id).\
    join(Artist, Show.artist_id==Artist.id).\
    filter(Show.start_time>=datetime.datetime.now()).\
    order_by(Show.start_time).\
    all()
  
  data=[]
  """
  print(event_query)
  data=[]
  for obj in event_query:
    print(obj)
    for x in obj.keys():

      print(x)
  """

  for row in event_query:
    show_event={

      "venue_id":row.venue_id,
      "venue_name": row.name,
      "artist_id":row.artist_id,
      "artist_name":row.artist_name,
      "artist_image_link":row.image_link,
      "start_time":row.start_time.strftime("%m/%d/%Y, %H:%M"),
      }
    data.append(show_event ) 
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  form = ShowForm(request.form, meta={'csrf': False})
  
  if form.validate():
    try:
      new_show= Show()
      form.populate_obj(new_show)
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except ValueError as e:
      print(e)
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    message=[]
    for field, err, in form.errors.items():
      message.append(field+' '+'|'.join(err))
      flash('Errors ' + str(message))


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
