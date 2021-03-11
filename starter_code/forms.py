from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, RadioField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, AnyOf, URL
# file to regex
import re 
# Utilities list
state_choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
]

genres_choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
]


# function to validate the number
def is_valid_phone(number):
    """ Validate phone numbers like:
    1234567890 - no space
    123.456.7890 - dot separator
    123-456-7890 - dash separator
    123 456 7890 - space separator

    Patterns:
    000 = [0-9]{3}
    0000 = [0-9]{4}
    -.  = ?[-. ]

    Note: (? = optional) - Learn more: https://regex101.com/
    """
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)

class ShowForm(Form):
    artist_id = IntegerField(
        'artist_id',
        validators=[DataRequired()]
    )
    

    venue_id = IntegerField(
        'venue_id',
        validators=[DataRequired()]
    )
    #in my modle its name is day_show
    # original verson start_time
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class DefaultForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    
    phone = StringField(
        'phone'
    )
    
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres',
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        # TODO implement enum restriction
        'website', validators=[URL()]
    )
    image_link = StringField(
        'image_link', validators=[URL(),DataRequired(),]
    )
    
    seeking_description=TextAreaField('seeking_description',)

    # functio to validate the field
    def validate(self):
        """Define a custom validate method in your Form:"""
        rv = Form.validate(self)
        if not rv:
            return False
        if not is_valid_phone(self.phone.data):
            self.phone.errors.append('Invalid phone.')
            return False
        if not set(self.genres.data).issubset(set(dict(genres_choices))):
            self.genres.errors.append('Invalid genres.')
            #print('set choice', set(self.genres.data))
            #print('genres_choices', set(dict(genres_choices)))
            return False
        if self.state.data not in set(dict (state_choices)):
            self.state.errors.append('Invalid state.')
            #print('set choice', self.state.data)
            #print('state_choices', set(dict(state_choices)))
            return False
        # if pass validation
        return True
    
class VenueForm(DefaultForm):
    address = StringField(
        'address', validators=[DataRequired()]
    )
    seeking_talent=RadioField(
        'seeking_talent', 
        choices=[
            ('True','Yes'),
            ('False','No'),
        ]
    )
    pass

class ArtistForm(DefaultForm):
    seeking_venue=RadioField(
        'seeking_venue', 
        choices=[
            ('True','Yes'),
            ('False','No'),
        ]
    )
    pass

# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
