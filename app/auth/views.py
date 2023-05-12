from flask import jsonify, request, session, abort
from flask_login import login_required, login_user, logout_user

from . import auth
from .. import db
from ..models import Customer


@auth.route('/register', methods=['POST'])
def register():
    customername = request.json.get('customername')
    birthday = request.json.get('birthday')
    phonenumber = request.json.get('phonenumber')
    account = request.json.get('account')
    password = request.json.get('password')
    if account is None or password is None:
        abort(400)  # missing arguments
    if Customer.query.filter_by(account=account).first() is not None:
        abort(400)  # existing user
    newuser = Customer(
        customername=customername,
        birthday=birthday,
        phonenumber=phonenumber,
        account=account,
        password=password
    )

    db.session.add(newuser)
    db.session.commit()

    return jsonify({'message': 'Sign Up Success'})


@auth.route('/login', methods=['POST'])
def login():
    account = request.json.get('account')
    password = request.json.get('password')

    customer = Customer.query.filter_by(account=account, hide=False).first_or_404()
    if customer is not None and customer.verify_password(password):
        login_user(customer)

        if customer.isadmin:
            return jsonify({'message': 'You are already logged in with admin permission'}),401
        else:
            return jsonify({'message': 'You are already logged in'})

    else:
        return jsonify({'message': 'Invalid email or password.'})

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()

    return jsonify({'message':'You have successfully been logged out.'})