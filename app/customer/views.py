import sys
import json

from flask import jsonify, request, session, abort, make_response
from flask_cors import cross_origin
from flask_login import current_user, login_required
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import customer
from .. import db
from ..models import Customer


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    currentUserId = get_jwt_identity()
    currentUser = Customer.query.filter_by(id=currentUserId, hide=False).first_or_404()
    if not currentUser.isadmin:
        abort(403)


@customer.route('/customers', methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def list_customers():
    check_admin()

    customers = Customer.query.filter_by(hide=False).all()
    print(customers, file=sys.stderr)
    customersList = []

    for customer in customers:
        customerDict = {
            "customerid": customer.id,
            "customername": customer.customername,
            "phonenumber": customer.phonenumber,
            "birthday": customer.birthday,
            "account": customer.account,
            "createat": customer.createat
        }
        customersList.append(customerDict)
    if not customersList:
        return make_response(jsonify({'message': 'Customers is empty'}), 404)
    return make_response(jsonify({'customers': customersList}), 200)


@customer.route('/customers/<int:id>', methods=['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def get_customer_by_id(id):
    check_admin()

    customer = Customer.query.filter_by(id=id, hide=False).first_or_404()

    return make_response(jsonify({"customer":
        [{
            "customerid": customer.id,
            "customername": customer.customername,
            "birthday": customer.birthday,
            "phonenumber": customer.phonenumber,
            "account": customer.account,
            "createat": customer.createat
        }]
    }))


@customer.route('/customers/<int:id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
@jwt_required()
def edit_customer(id):
    check_admin()

    customer = Customer.query.get_or_404(id)

    customername = request.json.get('customername')
    birthday = request.json.get('birthday')
    phonenumber = request.json.get('phonenumber')

    customer.customername = customername
    customer.birthday = birthday
    customer.phonenumber = phonenumber
    db.session.commit()

    return make_response(jsonify({
        "customerid": customer.id,
        "customername": customer.customername,
        "birthday": customer.birthday,
        "phonenumber": customer.phonenumber
    }))


@customer.route('/customers/<int:id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@jwt_required()
def delete_customer(id):
    check_admin()

    customer = Customer.query.filter_by(id=id, hide=False).first_or_404()

    customer.hide = True

    db.session.commit()

    return make_response(jsonify({'message': 'Delete success'}))
