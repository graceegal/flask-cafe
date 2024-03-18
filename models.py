"""Data models for Flask Cafe"""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from mapping import save_map

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_CAFE_IMAGE = "/static/images/default-cafe.jpg"
DEFAULT_USER_IMAGE = "/static/images/default-pic.png"


class City(db.Model):
    """Cities for cafes."""

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )

    @classmethod
    def get_city_choices(cls):
        """ get all city choices from City model and return each
            as (code, City Name) in alphabetical order """

        cities = City.query.order_by(City.name).all()
        return [(city.code, city.name) for city in cities]


class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    url = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default=DEFAULT_CAFE_IMAGE,
    )

    city = db.relationship("City", backref='cafes')

    def __repr__(self):
        return f'<Cafe id={self.id} name="{self.name}">'

    def get_city_state(self):
        """Return 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'

    def save_map(self):
        """ Save map for specified cafe """

        save_map(self.id, self.address, self.city.name, self.city.state)


class User(db.Model, UserMixin):
    """ User information and credentials """

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    email = db.Column(
        db.String(50),
        nullable=False,
    )

    first_name = db.Column(
        db.String(30),
        nullable=False,
    )

    last_name = db.Column(
        db.String(30),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default=DEFAULT_USER_IMAGE,
    )

    password_hash = db.Column(
        db.Text,
        nullable=False,
    )

    liked_cafes = db.relationship(
        'Cafe', secondary="likes", backref="liking_users")

    def __repr__(self):
        return f'<User id={self.id} username="{self.username}">'

    def get_full_name(self):
        """Return 'first_name last_name' for user."""

        return f'{self.first_name} {self.last_name}'

    @classmethod
    def register(cls, username, email, first_name, last_name, password,
                 description='', image_url=DEFAULT_USER_IMAGE, admin=False):
        """Register a user, hashing their password."""

        #  FIXME: image URL is generating as '' instead of default (when app.py line 76 OR statement is removed)
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            description=description,
            image_url=image_url,
            password_hash=hashed_utf8,
            admin=admin,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        user = User.query.filter_by(username=username).one_or_none()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        else:
            return False


class Like(db.Model):
    """Join table between users and cafes (the join represents a like)."""

    __tablename__ = 'likes'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )

    cafe_id = db.Column(
        db.Integer,
        db.ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
