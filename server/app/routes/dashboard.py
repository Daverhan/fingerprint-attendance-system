from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.utilities.database import db
from app.models.organization import Organization, Event

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def dashboard():
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)
    events = organization.events.order_by(Event.date.desc()).all()

    return render_template('dashboard.html', organization=organization, events=events)


@dashboard_bp.route('/create_event', methods=['GET', 'POST'])
def create_event():
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)

    if request.method == 'GET':
        return render_template('create_event.html', organization=organization)

    if request.method == 'POST':
        required_fields = ['name']

        request_form_data = {field: request.form.get(
            field) for field in required_fields}

        if not all(request_form_data.get(field) for field in required_fields):
            return render_template('create_event.html', organization=organization, error_message="Missing required fields")

        event = Event(**{field: request_form_data[field]
                      for field in required_fields}, organization=organization)

        db.session.add(event)
        db.session.commit()

        return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)
    event = Event.query.get_or_404(id)

    if request.method == 'GET':
        return render_template('edit_event.html', organization=organization, event=event)

    if request.method == 'POST':
        event.name = request.form.get('name', event.name)

        db.session.commit()

        return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/view_event/<int:id>/')
def view_event(id):
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)
    event = Event.query.get_or_404(id)
    attendees = event.attendees.all()

    return render_template('view_event.html', organization=organization, event=event, attendees=attendees)


@dashboard_bp.route('/view_members')
def view_organization_members():
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)
    members = organization.members.all()

    return render_template('view_members.html', organization=organization, members=members)


@dashboard_bp.route('/delete_event/<int:id>', methods=['DELETE'])
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
