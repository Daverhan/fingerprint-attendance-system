from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.utilities.database import db
from app.models.models import Organization, Event

events_bp = Blueprint('events', __name__)


@events_bp.route('/')
def events():
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)
    events = organization.events.order_by(Event.date.desc()).all()

    return render_template('events/events.html', organization=organization, events=events)


@events_bp.route('/create', methods=['GET', 'POST'])
def create_event():
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)

    if request.method == 'GET':
        return render_template('events/create_event.html', organization=organization)

    if request.method == 'POST':
        required_fields = ['name']

        request_form_data = {field: request.form.get(
            field) for field in required_fields}

        if not all(request_form_data.get(field) for field in required_fields):
            return render_template('events/create_event.html', organization=organization, error_message="Missing required fields")

        event = Event(**{field: request_form_data[field]
                      for field in required_fields}, organization=organization)

        db.session.add(event)
        db.session.commit()

        return redirect(url_for('events.events'))


@events_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_event(id):
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)
    event = Event.query.get_or_404(id)

    if request.method == 'GET':
        return render_template('events/edit_event.html', organization=organization, event=event)

    if request.method == 'POST':
        event.name = request.form.get('name', event.name)

        db.session.commit()

        return redirect(url_for('events.events'))


@events_bp.route('/<int:id>/view')
def view_event(id):
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)
    event = Event.query.get_or_404(id)
    attendees = event.attendees.all()

    return render_template('events/view_event.html', organization=organization, event=event, attendees=attendees)


@events_bp.route('/<int:id>', methods=['DELETE'])
def delete_event(id):
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    event = Event.query.filter_by(
        id=id, organization_id=organization_id).first_or_404()

    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
