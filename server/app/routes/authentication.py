from flask import Blueprint, redirect, session, request, make_response, render_template, url_for
from app.utilities.database import db
from app.models.models import Account

authentication_bp = Blueprint('authentication', __name__)


@authentication_bp.route('/', methods=['GET', 'POST'])
def organization_login():
    if request.method == 'GET':
        return render_template('auth/index.html')

    if request.method == 'POST':
        required_fields = ['username', 'password']

        request_form_data = {field: request.form.get(
            field) for field in required_fields}

        if not all(request_form_data.get(field) for field in required_fields):
            return render_template('auth/index.html', error_message="Missing required fields")

        organization_account = db.session.query(Account).filter_by(
            **{field: request_form_data[field] for field in required_fields}).first()

        if not organization_account:
            return render_template('auth/index.html', error_message="Invalid username or password")

        session['organization_id'] = organization_account.organization_id

        return redirect(url_for('events.events'))


@authentication_bp.route('/logout')
def organization_logout():
    session.clear()
    response = make_response(redirect('/'))
    response.delete_cookie('session')
    return response
