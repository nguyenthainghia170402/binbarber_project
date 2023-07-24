from flask import jsonify, request, session, abort, make_response, g
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, unset_jwt_cookies, get_jwt_identity, jwt_required, \
    create_refresh_token
from flask_login import login_required, login_user, logout_user, current_user

import app
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
    session['user_id'] = newuser.id

    return {'message': 'Sign Up Success'},200


@auth.route('/login', methods=['POST'])
# @cross_origin(supports_credentials=True)
def login():
    account = request.json.get('account')
    password = request.json.get('password')

    customer = Customer.query.filter_by(account=account, hide=False).first()
    if customer is not None and customer.verify_password(password):
        login_user(customer, remember=True)
        access_token = create_access_token(identity=customer.id)
        new_refresh_token = create_refresh_token(identity=current_user.id)
        print(current_user)
        if customer.isadmin:
            response = make_response(jsonify({'message': 'You are already logged in with admin permission', 'access_token': access_token, 'user_id': customer.id}), 201)
            response.set_cookie('access_token_cookie', access_token, httponly=True, samesite='None', secure=True)
            response.headers.add('SameSite', 'None')
            response.headers.add('Secure', 'True')

            # session_cookie_name = app.config.get('SESSION_COOKIE_NAME')
            # session_cookie_domain = app.config.get('SESSION_COOKIE_DOMAIN')
            # session_cookie_secure = True if app.config.get('SESSION_COOKIE_SECURE') else None
            return response
        else:
            response = make_response(jsonify({'message': 'You are already logged in', 'access_token': access_token, 'user_id': customer.id}), 200)
            response.set_cookie('access_token_cookie', access_token, httponly=True, samesite='None', secure=True)
            response.headers.add('SameSite', 'None')
            response.headers.add('Secure', 'True')
            return response


    else:
        return {'message': 'Invalid email or password.'}, 400

@auth.route('/logout', methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def logout():
    response = make_response(jsonify({'message':'You have successfully been logged out.'}), 200)
    unset_jwt_cookies(response)
    return response

@auth.route('/customer', methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def get_current_customer():
    customerid = get_jwt_identity()
    customer = Customer.query.filter_by(id=customerid, hide=False).first_or_404()
    return {
        "customerid": customer.id,
        "customername": customer.customername,
        "birthday": customer.birthday,
        "phonenumber": customer.phonenumber
    }, 200