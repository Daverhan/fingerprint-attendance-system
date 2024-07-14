from flask import Blueprint, redirect, session, request, render_template, url_for, jsonify
from app.utilities.database import db
from app.models.models import Organization, Account, Attendee, Event

organizations_bp = Blueprint('organizations', __name__)


@organizations_bp.route('/create', methods=['GET', 'POST'])
def create_organization():
    if request.method == 'GET':
        return render_template('organizations/create_organization.html')

    if request.method == 'POST':
        organization_required_fields = ['name', 'pin']
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


@organizations_bp.route('/edit', methods=['GET', 'POST'])
def edit_organization():
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)

    if request.method == 'GET':
        return render_template('organizations/edit_organization.html', organization=organization)

    if request.method == 'POST':
        updatable_organization_fields = ['name', 'pin']

        for field in updatable_organization_fields:
            if request.form[field]:
                setattr(organization, field, request.form[field])

        if request.form['username']:
            organization_account_exists = Account.query.filter_by(
                username=request.form['username']).first() and organization.account.username != request.form['username']

            if organization_account_exists:
                return render_template('organizations/edit_organization.html', error_message="An organization already exists with the provided username", organization=organization)

            organization.account.username = request.form['username']

        if request.form['password'] or request.form['password_verify']:
            if request.form['password'] != request.form['password_verify']:
                return render_template('organizations/edit_organization.html', error_message="The inputted account password does not match the verified account password", organization=organization)

            organization.account.password = request.form['password']

        db.session.commit()

        return redirect(url_for('events.events'))


@organizations_bp.route('/<int:id>/create_member', methods=['POST'])
def create_member(id):
    Organization.query.get_or_404(id)
    request_form_data = request.get_json()

    required_fields = ['first_name', 'last_name', 'fingerprint_device_id']

    if not all(request_form_data.get(field) for field in required_fields):
        return 'Missing required fields', 400

    member_exists_in_organization = Attendee.query.filter_by(
        fingerprint_device_id=request_form_data['fingerprint_device_id'], organization_id=id).first()

    if member_exists_in_organization:
        return 'Fingerprint ID already exists in the hardware device for the provided organization', 400

    attendee = Attendee(
        **{field: request_form_data[field] for field in required_fields}, organization_id=id)

    db.session.add(attendee)
    db.session.commit()

    return 'Member successfully registered', 200


@organizations_bp.route('/<int:organization_id>/events/<int:event_id>/check-in/<int:fingerprint_device_id>', methods=['POST'])
def attendee_check_in(organization_id, event_id, fingerprint_device_id):
    organization = Organization.query.get_or_404(organization_id)
    event = Event.query.get_or_404(event_id)

    if event.organization_id != organization.id:
        return 'The provided event is not associated with the provided organization', 400

    attendee = Attendee.query.filter_by(
        fingerprint_device_id=fingerprint_device_id, organization_id=organization_id).first()

    if not attendee:
        return 'The provided Fingerprint ID does not exist in the provided organization', 404

    if attendee in event.attendees:
        return 'Attendee is already checked into the event', 400

    event.attendees.append(attendee)
    db.session.commit()

    return 'Check-in successful', 200


@organizations_bp.route('/<int:id>/verify-pin', methods=['POST'])
def verify_pin(id):
    pin = request.get_json()['pin']

    organization = Organization.query.get_or_404(id)

    if not pin:
        return 'Missing PIN number in the request', 400

    if organization.pin != pin:
        return 'Invalid PIN number', 400

    return 'Valid PIN number', 200
