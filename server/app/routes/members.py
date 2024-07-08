from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.utilities.database import db
from app.models.models import Organization, Attendee

members_bp = Blueprint('members', __name__)


@members_bp.route('/')
def members():
    organization_id = session.get('organization_id')

    if not organization_id:
        return redirect(url_for('authentication.organization_login'))

    organization = Organization.query.get_or_404(organization_id)
    members = organization.members.all()

    return render_template('members/view_members.html', organization=organization, members=members)


@members_bp.route('/<int:id>', methods=['DELETE'])
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
