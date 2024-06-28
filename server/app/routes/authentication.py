from flask import Blueprint, redirect, session, request, make_response, render_template, url_for
from app.utilities.database import db
from app.models.organization import Organization, Account

authentication_bp = Blueprint('authentication', __name__)


@authentication_bp.route('/', methods=['POST'])
def organization_login():
    required_fields = ['username', 'password']

    request_form_data = {field: request.form.get(
        field) for field in required_fields}

    if not all(request_form_data.get(field) for field in required_fields):
        return render_template('index.html', error_message="Missing required fields")

    organization_account = db.session.query(Account).filter_by(
        **{field: request_form_data[field] for field in required_fields}).first()

    if not organization_account:
        return render_template('index.html', error_message="Invalid username or password")

    session['organization_id'] = organization_account.organization_id

    return redirect(url_for('dashboard.dashboard'))


@authentication_bp.route('/create_organization', methods=['GET', 'POST'])
def create_organization():
    if request.method == 'GET':
        return render_template('create_organization.html')

    if request.method == 'POST':
        organization_required_fields = ['name']
        account_required_fields = ['username', 'password']

        request_form_data = {field: request.form.get(
            field) for field in organization_required_fields + account_required_fields}

        if not all(request_form_data.get(field) for field in organization_required_fields + account_required_fields):
            return render_template('create_organization.html', error_message="Missing required fields")

        organization_account_exists = Account.query.filter_by(
            username=request_form_data['username']).first()

        if organization_account_exists:
            return render_template('create_organization.html', error_message="An organization already exists with the provided username")

        organization = Organization(
            **{field: request_form_data[field] for field in organization_required_fields})
        account = Account(
            **{field: request_form_data[field] for field in account_required_fields}, organization=organization)

        db.session.add(organization)
        db.session.add(account)
        db.session.commit()

        session['organization_id'] = account.organization_id

        return redirect(url_for('dashboard.dashboard'))


@authentication_bp.route('/logout')
def organization_logout():
    session.clear()
    response = make_response(redirect('/'))
    response.delete_cookie('session')
    return response
