from app.main import bp_main
from flask import render_template, redirect, flash, url_for, \
    request, g, jsonify, current_app, abort, send_from_directory
from flask_login import current_user, login_required
from app import db
from datetime import datetime
from app.main.forms import ListingForm, MessageForm
import pathlib
import json
from werkzeug.utils import secure_filename
from app.models import User, Listing, Message, Notification
import os
from pathlib import Path
from flask import abort

@bp_main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.choices= ['Phones', 'Laptops & Computers', 'Appliances', 'Video Games', 'Books']

@bp_main.route('/', methods=['GET', 'POST'])
@bp_main.route('/index', methods=['GET', 'POST'])
def index():
    head = 'Recent Listings'
    page = request.args.get('page', 1, type=int)
    listings = Listing.query.filter_by(active=True).order_by(Listing.timestamp.desc()).paginate(page, current_app.config['LISTINGS_PER_PAGE'], False)
    next_url = url_for('main.index', page=listings.next_num) \
        if listings.has_next else None
    prev_url = url_for('main.index', page=listings.prev_num) \
        if listings.has_prev else None
    return render_template('index.html', title='Home', listings=listings.items, next_url=next_url, prev_url=prev_url, head=head)


@bp_main.route('/list_form', methods=['GET', 'POST'])
def list_form():
    form = ListingForm()
    return render_template('list_form.html', form=form)


@bp_main.route('/list', methods=['POST'])
def list():
    # check if the user has provided a title for
    form = ListingForm()
    if form.validate_on_submit():
        title = form.list_title.data
        description = form.description.data
        photos = form.inputFile.data
        category = form.category.data
        email=current_user.email
        owner = current_user.username
        currency = form.currency.data
        price = form.item_price.data
        item_name = form.item_name.data
        item_price = currency + str(price)
    photonames = []
    for photo in photos:
        photoname = filename = str(datetime.utcnow().date()) + '_' + str(datetime.utcnow().time()).replace(':', '.') + secure_filename(photo.filename)
        if photoname != '':
            photo_ext = os.path.splitext(photoname)[1]
            if photo_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                return "Invalid Image", 400
        photonames.append(photoname)

    name = json.dumps(photonames)
    new_listing = Listing(name=name, title=title, description=description, category=category, listing_email=email,
    listing_owner=owner, item_name=item_name, item_price=item_price)
    db.session.add(new_listing)
    db.session.commit()

    posted_listing = Listing.query.filter_by(name=name).first_or_404()
    listing_id = str(posted_listing.id)

    pathlib.Path(current_app.config['UPLOAD_PATH'], listing_id).mkdir(exist_ok=True)

    uniquenames=[]
    for photo in photos:
        filename = str(datetime.utcnow().date()) + '_' + str(datetime.utcnow().time()).replace(':', '.') + secure_filename(photo.filename)
        photo.save(os.path.join(current_app.config['UPLOAD_PATH'], listing_id,  filename))
        uniquenames.append(filename)
    name = json.dumps(photonames)
    the_listing = Listing.query.filter_by(id=int(listing_id)).first()
    the_listing.name=name
    db.session.commit()
    flash('Your Listing has been posted successfully!')
    return redirect(url_for('main.index'))


@bp_main.route('/upload/<photoname>/<id>')
def upload(photoname, id):
    if Path(current_app.config['UPLOAD_PATH'], str(id)).is_dir():
        image = send_from_directory(os.path.join(current_app.config['UPLOAD_PATH'], id), photoname)
        return image
    return


@bp_main.route('/view/<category>', methods=['GET', 'POST'])
def category(category):
    choices =  ['Phones', 'Laptops & Computers', 'Appliances', 'Video Games', 'Books']
    if category not in choices:
        abort(404)

    head = category
    page = request.args.get('page', 1, type=int)
    listings = Listing.query.filter_by(active=True, category=category).order_by(Listing.timestamp.desc()).paginate(page, current_app.config['LISTINGS_PER_PAGE'], False)
    next_url = url_for('main.index', page=listings.next_num) \
        if listings.has_next else None
    prev_url = url_for('main.index', page=listings.prev_num) \
        if listings.has_prev else None

    return render_template('index.html', listings=listings.items, next_url=next_url, prev_url=prev_url, head=head)

@bp_main.route('/view/<listing_id>/<name>')
def listing(listing_id, name):
    listed = Listing.query.filter_by(id=listing_id).first_or_404()
    user=User.query.filter_by(username=listed.listing_owner).first_or_404()
    return render_template('listing.html', listing=listed, user=user)


@bp_main.route('/user/<username>')
def user(username):
    user=User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    return render_template('user.html', user=user)



@bp_main.route('/notifications')
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])