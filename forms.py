"""Forms for Flask Cafe."""

from wtforms import StringField, TextAreaField, SelectField, PasswordField
from wtforms.validators import InputRequired, URL, Email, Optional, Length
from flask_wtf import FlaskForm
from models import City


class CSRFProtection(FlaskForm):
    """CSRFProtection form, intentionally has no fields."""


# TODO: add __Init__ so that city choices populate automatically every time instance of form is called
class AddEditCafeForm(FlaskForm):
    """ Form for adding & editing cafes """

    name = StringField(
        "Name",
        validators=[InputRequired()],
    )

    description = TextAreaField(
        "Description",
    )

    url = StringField(
        "URL",
        validators=[Optional(), URL()],
    )

    address = StringField(
        "Address",
        validators=[InputRequired()],
    )

    city_code = SelectField(
        "City"
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()]
    )


class SignUpForm(FlaskForm):
    """ Form for signing up as a new user """

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=20)],
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=30)],
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=30)],
    )

    description = TextAreaField(
        "Description"
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=50)],
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6)],
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()],
    )


class LogInForm(FlaskForm):
    """ Form for logging in as an existing user """

    username = StringField(
        "Username",
        validators=[InputRequired()],
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired()],
    )


class ProfileEditForm(FlaskForm):
    """ Form for editing an existing user's info
    (same as signup but no username or password) """

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=30)],
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=30)],
    )

    description = TextAreaField(
        "Description"
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=50)],
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()],
    )
