from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.utilities.database import db
from app.models.organization import Organization, Event, Attendee

attendee_management_bp = Blueprint('attendee_management', __name__)


@attendee_management_bp.route('/organization/<int:id>/create_member', methods=['POST'])
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


@attendee_management_bp.route('/organization/<int:organization_id>/event/<int:event_id>/check-in', methods=['POST'])
def event_check_in(organization_id, event_id):
    organization = Organization.query.get_or_404(organization_id)
    event = Event.query.get_or_404(event_id)

    if event.organization_id != organization.id:
        return jsonify({'error': 'The provided event is not associated with the provided organization'})

    request_form_data = request.get_json()

    if not request_form_data.get('fingerprint_device_id'):
        return jsonify({'error': 'Missing Fingerprint ID'})

    attendee = Attendee.query.filter_by(
        fingerprint_device_id=request_form_data['fingerprint_device_id'], organization_id=organization_id).first()

    if not attendee:
        return jsonify({'error': 'The provided Fingerprint ID does not exist in the provided organization'})

    if attendee in event.attendees:
        return jsonify({'error': 'Attendee is already checked into the event'})

    event.attendees.append(attendee)
    db.session.commit()

    return jsonify({'message': 'Check-in successful'})


@attendee_management_bp.route('/delete_member/<int:id>', methods=['DELETE'])
def delete_member(id):
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    attendee = Attendee.query.filter_by(
        id=id, organization_id=organization_id).first_or_404()

    if attendee:
        db.session.delete(attendee)
        db.session.commit()
        return jsonify({'message': 'Member deleted successfully'}), 200
