from app.utilities.database import db

MAX_FIRST_NAME_LENGTH = 100
MAX_LAST_NAME_LENGTH = 100
MAX_EVENT_NAME = 100
MAX_ORGANIZATION_NAME = 100


event_attendee = db.Table('event_attendee', db.Column('event_id', db.Integer, db.ForeignKey(
    'event.id'), primary_key=True), db.Column('attendee_id', db.Integer, db.ForeignKey('attendee.id'), primary_key=True))


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(
        db.String(MAX_ORGANIZATION_NAME), nullable=False)
    events = db.relationship('Event', backref='organization', lazy='dynamic')


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey(
        'organization.id'), nullable=False)
    event_name = db.Column(db.String(MAX_EVENT_NAME), nullable=False)
    attendees = db.relationship(
        'Attendee', secondary=event_attendee, backref=db.backref('events', lazy='dynamic'), lazy='dynamic')


class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(MAX_FIRST_NAME_LENGTH), nullable=False)
    last_name = db.Column(db.String(MAX_LAST_NAME_LENGTH), nullable=False)
