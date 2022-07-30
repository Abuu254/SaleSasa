from app import db, login
from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os
from pathlib import Path
from flask import current_app, url_for
import json
from time import time

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    listings = db.relationship('Listing', backref='owner', lazy='dynamic')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_notification_time = db.Column(db.DateTime)
    last_message_unread_time = db.Column(db.DateTime)
    friends = db.relationship('Chats',
                                    foreign_keys='Chats.contact_id',
                                    backref='friend', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def user_active_listings(self):
        listings = Listing.query.filter_by(listing_owner=self.username, active=True).all()
        return listings

    def user_inactive_listings(self):
        listings = Listing.query.filter_by(listing_owner=self.username, active=False).all()
        return listings
    def user_bought_listings(self):
        listings = Listing.query.filter_by(buyer=self.username, active=False).all()
        return listings

    def new_messages_notification(self):
        last_seen_time = self.last_message_notification_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient_id=self.id).filter(
            Message.timestamp > last_seen_time).count()

    def new_messages_unread(self):
        last_seen_time = self.last_message_unread_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient_id=self.id).filter(
            Message.timestamp > last_seen_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Listing(db.Model):
    id = db.Column(db.Integer,  primary_key=True)
    title = db.Column(db.String(140))
    category = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    item_name = db.Column(db.String(128), nullable=False)
    item_price = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, unique=False, default=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    listing_email= db.Column(db.String(128))
    listing_owner= db.Column(db.String(64))
    buyer = db.Column(db.String(64))


    def __repr__(self):
        return '<Listing {}>'.format(self.category)

    def post_images(self):
        if Path(current_app.config['UPLOAD_PATH'], str(self.id)).is_dir():
            images = os.listdir(os.path.join(current_app.config['UPLOAD_PATH'], str(self.id)))
            if images:
                return images
            return None

    def listing_avatar(self, size):
        digest = md5(self.listing_email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


class Chats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Chats {}>'.format(self.id)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_username = db.Column(db.String(64))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_link = db.Column(db.Integer, db.ForeignKey('chats.room_id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)