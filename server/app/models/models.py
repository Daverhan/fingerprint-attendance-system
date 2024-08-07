from app.utilities.database import db
from datetime import datetime
from sqlalchemy import DateTime

MAX_FIRST_NAME_LENGTH = 100
MAX_LAST_NAME_LENGTH = 100
MAX_EVENT_NAME_LENGTH = 100
MAX_ORGANIZATION_NAME_LENGTH = 100
MAX_ORGANIZATION_PIN_LENGTH = 8
MAX_ACCOUNT_USERNAME_LENGTH = 64
MAX_ACCOUNT_PASSWORD_LENGTH = 100


event_attendee = db.Table('event_attendee', db.Column('event_id', db.Integer, db.ForeignKey(
    'event.id'), primary_key=True), db.Column('attendee_id', db.Integer, db.ForeignKey('attendee.id'), primary_key=True))


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(MAX_ORGANIZATION_NAME_LENGTH), nullable=False)
    pin = db.Column(db.String(MAX_ORGANIZATION_PIN_LENGTH), nullable=False)
    account = db.relationship('Account', backref='organization', uselist=False)
    events = db.relationship('Event', backref='organization', lazy='dynamic')
    members = db.relationship(
        'Attendee', backref='organization', lazy='dynamic')


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey(
        'organization.id'), nullable=False, unique=True)
    username = db.Column(
        db.String(MAX_ACCOUNT_USERNAME_LENGTH), nullable=False)
    password = db.Column(
        db.String(MAX_ACCOUNT_PASSWORD_LENGTH), nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey(
        'organization.id'), nullable=False)
    name = db.Column(db.String(MAX_EVENT_NAME_LENGTH), nullable=False)
    date = db.Column(DateTime, default=datetime.now, nullable=False)
    attendees = db.relationship(
        'Attendee', secondary=event_attendee, backref=db.backref('events', lazy='dynamic'), lazy='dynamic')


class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey(
        'organization.id'), nullable=False)
    fingerprint_device_id = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(MAX_FIRST_NAME_LENGTH), nullable=False)
    last_name = db.Column(db.String(MAX_LAST_NAME_LENGTH), nullable=False)
