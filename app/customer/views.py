import sys
import json

from flask import jsonify, request, session, abort, make_response
from flask_login import current_user, login_required
from datetime import datetime

from . import customer
from .. import db
from ..models import Customer

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.isadmin:
        abort(403)

@customer.route('/customers', methods = ['GET'])
@login_required
def list_customers():
    check_admin()

    customers = Customer.query.filter_by(hide=False).all()
    print(customers, file=sys.stderr)
    customersList = []

    for customer in customers:
        customerDict = {
            "customerid" : customer.customerid,
            "customername" : customer.customername,
            "phonenumber" : customer.phonenumber,
            "birthday": customer.birthday,
            "account": customer.account,
            "createat" : customer.createat
        }
        customersList.append(customerDict)

    return jsonify({'customers' : customersList})

@customer.route('/customers/<int:id>', methods = ['GET'])
@login_required
def get_customer_by_id(id):
    check_admin()

    customer = Customer.query.filter_by(customerid=id, hide=False).first_or_404()

    return make_response(jsonify({"customer":
        [{
            "customerid": customer.customerid,
            "customername": customer.customername,
            "birthday": customer.birthday,
            "phonenumber": customer.phonenumber,
            "account": customer.account,
            "createat": customer.createat
        }]
    }))


@customer.route('/customers/<int:id>', methods = ['PUT'])
@login_required
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
        "customerid": customer.customerid,
        "customername": customer.customername,
        "birthday": customer.birthday,
        "phonenumber": customer.phonenumber
    }))

@customer.route('/customers/<int:id>', methods = ['DELETE'])
@login_required
def delete_customer(id):
    check_admin()

    customer = Customer.query.filter_by(customerid=id, hide=False).first_or_404()

    customer.hide = True

    db.session.commit()

    return make_response(jsonify({'message': 'Delete success'}))