"""Flask App for Flask Cafe."""

import os

from flask import Flask, render_template, redirect, url_for, flash, g, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from models import connect_db, db, City, DEFAULT_CAFE_IMAGE, Cafe, DEFAULT_USER_IMAGE, User
from forms import CSRFProtection, AddEditCafeForm, SignUpForm, LogInForm, ProfileEditForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_cafe')
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")
app.config['SQLALCHEMY_ECHO'] = True

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
# toolbar = DebugToolbarExtension(app)

connect_db(app)


#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = NOT_LOGGED_IN_MSG
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.before_request
def add_csrf_only_form():
    """Add a CSRF-only form so that every route can use it."""

    g.csrf_form = CSRFProtection()


#######################################
# user routes- login, signup, logout

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """ Handle user signup.

    Create new user and add to DB. Redirect to cafe list page.

    If form not valid, present form with error messages.

    If there already is a user with that username: flash message
    and re-present form. """

    if current_user:
        logout_user()

    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        description = form.description.data
        image_url = form.image_url.data or DEFAULT_USER_IMAGE
        password = form.password.data

        user = User.register(username, email, first_name,
                             last_name, password, description, image_url)

        try:
            db.session.commit()

        except IntegrityError:
            flash("Username already taken.", 'danger')
            return render_template("auth/signup-form.html", form=form)

        login_user(user)

        flash('You are signed up and logged in.', 'success')
        return redirect(url_for("cafe_list"))

    return render_template("auth/signup-form.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Handle user login and redirect to cafe list page on success. """

    if current_user.is_authenticated:
        logout_user()

    form = LogInForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data,
        )

        if user:
            login_user(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for("cafe_list"))

        flash("Invalid credentials.", 'danger')

    return render_template('auth/login-form.html', form=form)


@app.post('/logout')
@login_required
def logout():
    """Handle logout of user and redirect to homepage."""

    form = g.csrf_form

    if form.validate_on_submit():
        logout_user()
        flash("You have successfully logged out.", "success")
    else:
        flash("Access unauthorized.", "danger")

    return redirect(url_for("homepage"))


#######################################
# homepage & error handler

@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


#######################################
# profile

@app.get('/profile')
@login_required
def show_profile():
    """ show profile page of logged in user """

    return render_template('profile/detail.html')


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """ GET: Show form for editing a user profile

        POST: Handle editing a profile from form submit.
        Redirect and alert user if profile was successfully edited."""

    user = current_user
    image = user.image_url if user.image_url != DEFAULT_USER_IMAGE else ''

    form = ProfileEditForm(
        first_name=user.first_name,
        last_name=user.last_name,
        description=user.description,
        email=user.email,
        image_url=image
    )

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.description = form.description.data or ''
        user.email = form.email.data
        user.image_url = form.image_url.data or DEFAULT_USER_IMAGE

        db.session.commit()

        flash('Profile edited.', 'success')
        redirect_url = url_for('show_profile')
        return redirect(redirect_url)

    return render_template(
        'profile/edit-form.html',
        form=form
    )


#######################################
# cafes


@app.get('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
    )


@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template(
        'cafe/detail.html',
        cafe=cafe,
    )


@app.route('/cafes/add', methods=['GET', 'POST'])
def add_cafe():
    """ If user is not logged in and an admin, redirect them to homepage, otherwise:

        GET: Show form for adding a cafe.

        POST: Handle adding a new cafe from form submit.
        Redirect and alert user if cafe was successfully added."""

    if (not current_user.is_authenticated) or (current_user.is_authenticated and not current_user.admin):
        flash('Unauthorized. Please login with admin credentials to view page.', 'danger')
        return redirect('/')

    form = AddEditCafeForm()
    form.city_code.choices = City.get_city_choices()

    if form.validate_on_submit():
        # Reference for data comprehension: adoption agency solution
        data = {k: v if v != "" else None for k,
                v in form.data.items() if k != "csrf_token"}
        cafe = Cafe(**data)

        db.session.add(cafe)

        db.session.flush()
        cafe.save_map()

        db.session.commit()

        flash(f'{cafe.name} added.', "success")
        redirect_url = url_for('cafe_detail', cafe_id=cafe.id)
        return redirect(redirect_url)

    return render_template(
        'cafe/add-form.html',
        form=form
    )


@app.route('/cafes/<int:cafe_id>/edit', methods=['GET', 'POST'])
def edit_cafe(cafe_id):
    """ If user is not logged in and an admin, redirect them to homepage, otherwise:

        GET: Show form for editing a cafe

        POST: Handle editing a cafe from form submit.
        Redirect and alert user if cafe was successfully edited. """

    if (not current_user.is_authenticated) or (current_user.is_authenticated and not current_user.admin):
        flash('Unauthorized. Please login with admin credentials to view page.', 'danger')
        return redirect('/')

    cafe = Cafe.query.get_or_404(cafe_id)
    form = AddEditCafeForm(obj=cafe)
    form.city_code.choices = City.get_city_choices()

    if form.validate_on_submit():
        cafe.name = form.name.data
        cafe.description = form.description.data or ''
        cafe.url = form.url.data or ''
        cafe.address = form.address.data
        cafe.city_code = form.city_code.data
        cafe.image_url = form.image_url.data or DEFAULT_CAFE_IMAGE

        cafe.save_map()

        db.session.commit()

        flash(f'{cafe.name} edited.', 'success')
        redirect_url = url_for('cafe_detail', cafe_id=cafe_id)
        return redirect(redirect_url)

    return render_template(
        'cafe/edit-form.html',
        form=form,
        cafe=cafe
    )


#######################################
# API for liking/unliking cafes


@app.get('/api/likes')
def get_like_status():
    """ """

    if not current_user.is_authenticated:
        return jsonify({"error": "Not logged in"})
    else:
        cafe_id = request.args.get('cafe_id')
        cafe = Cafe.query.get_or_404(cafe_id)

        if cafe in current_user.liked_cafes:
            return jsonify({"likes": True})
        else:
            return jsonify({"likes": False})


@app.post('/api/like')
def like_cafe():
    """ """

    if not current_user.is_authenticated:
        return jsonify({"error": "Not logged in"})
    else:
        data = request.json
        cafe_id = data.get('cafe_id')
        cafe = Cafe.query.get_or_404(cafe_id)

        current_user.liked_cafes.append(cafe)

        db.session.commit()

        return jsonify({"liked": cafe_id})


@app.post('/api/unlike')
def unlike_cafe():
    """ """

    if not current_user.is_authenticated:
        return jsonify({"error": "Not logged in"})
    else:
        data = request.json
        cafe_id = data.get('cafe_id')
        cafe = Cafe.query.get_or_404(cafe_id)

        current_user.liked_cafes.remove(cafe)

        db.session.commit()

        return jsonify({"unliked": cafe_id})
