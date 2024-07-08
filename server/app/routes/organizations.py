from flask import Blueprint, redirect, session, request, render_template, url_for, jsonify
from app.utilities.database import db
from app.models.models import Organization, Account, Attendee, Event

organizations_bp = Blueprint('organizations', __name__)


@organizations_bp.route('/create', methods=['GET', 'POST'])
def create_organization():
    if request.method == 'GET':
        return render_template('organizations/create_organization.html')

    if request.method == 'POST':
        organization_required_fields = ['name']
        account_required_fields = ['username', 'password']

        request_form_data = {field: request.form.get(
            field) for field in organization_required_fields + account_required_fields}

        if not all(request_form_data.get(field) for field in organization_required_fields + account_required_fields):
            return render_template('organizations/create_organization.html', error_message="Missing required fields")

        organization_account_exists = Account.query.filter_by(
            username=request_form_data['username']).first()

        if organization_account_exists:
            return render_template('organizations/create_organization.html', error_message="An organization already exists with the provided username")

        organization = Organization(
            **{field: request_form_data[field] for field in organization_required_fields})
        account = Account(
            **{field: request_form_data[field] for field in account_required_fields}, organization=organization)

        db.session.add(organization)
        db.session.add(account)
        db.session.commit()

        session['organization_id'] = account.organization_id

        return redirect(url_for('events.events'))


@organizations_bp.route('/<int:id>/create_member', methods=['POST'])
def create_member(id):
    request_form_data = request.get_json()

    required_fields = ['first_name', 'last_name', 'fingerprint_device_id']

    if not all(request_form_data.get(field) for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    member_exists_in_organization = Attendee.query.filter_by(
        fingerprint_device_id=request_form_data['fingerprint_device_id'], organization_id=id).first()

    if member_exists_in_organization:
        return jsonify({'error': 'Fingerprint ID already exists in the hardware device for the provided organization'}), 400

    attendee = Attendee(
        **{field: request_form_data[field] for field in required_fields}, organization_id=id)

    db.session.add(attendee)
    db.session.commit()

    return jsonify({'message': 'Member successfully registered'}), 200


@organizations_bp.route('/<int:organization_id>/events/<int:event_id>/check-in/<int:fingerprint_device_id>', methods=['POST'])
def attendee_check_in(organization_id, event_id, fingerprint_device_id):
    organization = Organization.query.get_or_404(organization_id)
    event = Event.query.get_or_404(event_id)

    if event.organization_id != organization.id:
        return jsonify({'error': 'The provided event is not associated with the provided organization'}), 400

    attendee = Attendee.query.filter_by(
        fingerprint_device_id=fingerprint_device_id, organization_id=organization_id).first()

    if not attendee:
        return jsonify({'error': 'The provided Fingerprint ID does not exist in the provided organization'}), 404

    if attendee in event.attendees:
        return jsonify({'error': 'Attendee is already checked into the event'}), 400

    event.attendees.append(attendee)
    db.session.commit()

    return jsonify({'message': 'Check-in successful'}), 200