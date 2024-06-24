from flask import Blueprint, render_template
from app.models.organization import Organization

organization_bp = Blueprint('organization', __name__)


@organization_bp.route('/<int:organization_id>/dashboard')
def dashboard(organization_id):
    organization = Organization.query.get_or_404(organization_id)

    return render_template('dashboard.html', organization=organization)
