import sys
import json

from flask import jsonify, request, session, abort, make_response
from flask_cors import cross_origin
from flask_login import current_user, login_required
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import service
from .. import db
from ..models import Service, Customer


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    currentUser = Customer.query.filter_by(id=get_jwt_identity(), hide=False).first_or_404()
    if not currentUser.isadmin:
        abort(403)

@service.route('/services', methods = ['GET'])
@cross_origin(supports_credentials=True)
# @jwt_required()
def list_services():
    # check_admin()

    services = Service.query.filter_by(hide=False).all()
    print(services, file=sys.stderr)
    servicesList = []

    for service in services:
        serviceDict = {
            "serviceid" : service.serviceid,
            "servicename" : service.servicename,
            "timeofservice" : service.timeofservice,
            "price" : service.price,
            "createat" : service.createat,
            "image": service.image
        }
        servicesList.append(serviceDict)
    if not servicesList:
        return make_response(jsonify({'message' : 'Services is empty'}), 404)
    return make_response(jsonify({'services' : servicesList}), 200)

@service.route('/services/<int:id>', methods = ['GET'])
@cross_origin(supports_credentials=True)
@jwt_required()
def get_service_by_id(id):
    check_admin()

    service = Service.query.filter_by(serviceid=id, hide=False).first_or_404()

    return make_response(jsonify({"service":
        {
            "serviceid": service.serviceid,
            "servicename" : service.servicename,
            "timeofservice" : service.timeofservice,
            "price" : service.price,
            "createat" : service.createat
        }
    }))


@service.route('/services', methods=['POST'])
@cross_origin(supports_credentials=True)
# @jwt_required()
def create_service():
    # check_admin()
    servicename = request.json.get('servicename')
    timeofservice = request.json.get('timeofservice')
    price = request.json.get('price')
    if servicename is None or timeofservice is None or price is None:
        abort(400)  # missing arguments

    newservice = Service(
        servicename=servicename,
        timeofservice=timeofservice,
        price=price
    )

    db.session.add(newservice)
    db.session.commit()

    return make_response(jsonify({'message': 'Create new service Success'}), 200)

@service.route('/services/<int:id>', methods = ['PUT'])
@cross_origin(supports_credentials=True)
@jwt_required()
def edit_service(id):
    check_admin()

    service = Service.query.get_or_404(id)

    servicename = request.json.get('servicename')
    timeofservice = request.json.get('timeofservice')
    price = request.json.get('price')

    service.servicename = servicename
    service.timeofservice = timeofservice
    service.price = price
    db.session.commit()

    return make_response(jsonify({"service":
        [{
            "serviceid" : service.serviceid,
            "servicename" : service.servicename,
            "timeofservice" : service.timeofservice,
            "price" : service.price,
            "createat" : service.createat
        }]
    }))

@service.route('/services/<int:id>', methods = ['DELETE'])
@cross_origin(supports_credentials=True)
@jwt_required()
def delete_service(id):
    check_admin()

    service = Service.query.filter_by(serviceid=id, hide=False).first_or_404()

    service.hide = True

    db.session.commit()

    return make_response(jsonify({'message': 'Delete success'}))