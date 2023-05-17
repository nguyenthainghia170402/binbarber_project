import sys
import json

from flask import jsonify, request, session, abort, make_response
from flask_login import current_user, login_required
from datetime import datetime

from . import barber
from .. import db
from ..models import Barber

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.isadmin:
        abort(403)

@barber.route('/barbers', methods = ['GET'])
@login_required
def list_barbers():
    check_admin()

    barbers = Barber.query.filter_by(hide=False).all()
    print(barbers, file=sys.stderr)
    barbersList = []

    if not barbers:
        return make_response(jsonify({'message' : 'Barbers is empty'}), 404)

    for barber in barbers:
        customerDict = {
            "barberid" : barber.barberid,
            "barbername" : barber.barbername,
            "phonenumber" : barber.phonenumber,
            "address" : barber.address,
            "birthday": barber.birthday,
            "forte": barber.forte,
            "description": barber.description,
            "image": barber.image,
            "createat" : barber.createat
        }
        barbersList.append(customerDict)
    if not barbersList:
        return make_response(jsonify({'message' : 'Barbers is empty'}), 404)

    return jsonify({'barbers' : barbersList})

@barber.route('/barbers/<int:id>', methods = ['GET'])
@login_required
def get_barber_by_id(id):
    check_admin()

    barber = Barber.query.filter_by(barberid=id, hide=False).first_or_404()

    return make_response(jsonify({"barber":
        [{
            "barberid": barber.barberid,
            "barbername": barber.barbername,
            "birthday": barber.birthday,
            "phonenumber": barber.phonenumber,
            "address": barber.address,
            "forte": barber.forte,
            "description": barber.description,
            "image": barber.image,
            "createat": barber.createat
        }]
    }))

@barber.route('/barbers', methods=['POST'])
def create_barber():
    barbername = request.json.get('barbername')
    birthday = request.json.get('birthday')
    phonenumber = request.json.get('phonenumber')
    address = request.json.get('address')
    forte = request.json.get('forte')
    description = request.json.get('description')
    image = request.json.get('image')
    if barbername is None or phonenumber is None or forte is None or description is None or image is None:
        abort(400)  # missing arguments

    newbarber = Barber(
        barbername=barbername,
        birthday=birthday,
        phonenumber=phonenumber,
        address=address,
        forte=forte,
        description=description,
        image=image
    )

    db.session.add(newbarber)
    db.session.commit()

    return make_response(jsonify({'message': 'Create new barber Success'}), 200)

@barber.route('/barbers/<int:id>', methods = ['PUT'])
@login_required
def edit_barber(id):
    check_admin()

    barber = Barber.query.get_or_404(id)

    barbername = request.json.get('barbername')
    birthday = request.json.get('birthday')
    phonenumber = request.json.get('phonenumber')
    address = request.json.get('address')
    forte = request.json.get('forte')
    description = request.json.get('description')
    image = request.json.get('image')

    barber.barbername = barbername
    barber.birthday = birthday
    barber.phonenumber = phonenumber
    barber.address = address
    barber.forte = forte
    barber.description = description
    barber.image = image
    db.session.commit()

    return make_response(jsonify({"barber":
        [{
            "barberid": barber.barberid,
            "barbername": barber.barbername,
            "birthday": barber.birthday,
            "phonenumber": barber.phonenumber,
            "address": barber.address,
            "forte": barber.forte,
            "description": barber.description,
            "image": barber.image,
            "createat": barber.createat
        }]
    }))

@barber.route('/barbers/<int:id>', methods = ['DELETE'])
@login_required
def delete_barber(id):
    check_admin()

    barber = Barber.query.filter_by(barberid=id, hide=False).first_or_404()

    barber.hide = True

    db.session.commit()

    return make_response(jsonify({'message': 'Delete success'}))