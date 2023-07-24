import os
import sys
import json
import shutil
from flask import jsonify, request, session, abort, make_response
from flask_cors import cross_origin
from flask_login import current_user, login_required
from datetime import datetime
from flask_jwt_extended import create_access_token, unset_jwt_cookies, get_jwt_identity, jwt_required

from . import barber
from .. import db
from ..models import Barber, Customer


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    currentUser = Customer.query.filter_by(id=get_jwt_identity(), hide=False).first_or_404()
    if not currentUser.isadmin:
        abort(403)
@barber.route('/barbers', methods = ['GET'])
def list_barbers():

    barbers = Barber.query.filter_by(hide=False).all()
    print(barbers, file=sys.stderr)
    barbersList = []

    if not barbers:
        return make_response(jsonify({'message' : 'Barbers is empty'}), 404)

    for barber in barbers:
        barberDict = {
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
        barbersList.append(barberDict)
    if not barbersList:
        return make_response(jsonify({'message' : 'Barbers is empty'}), 404)

    return jsonify({'barbers' : barbersList})

@barber.route('/barbers/<int:id>', methods = ['GET'])
def get_barber_by_id(id):

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
@cross_origin(supports_credentials=True)
@jwt_required()
def create_barber():
    # check_admin()
    barbername = request.json.get('barbername')
    birthday = request.json.get('birthday')
    phonenumber = request.json.get('phonenumber')
    address = request.json.get('address')
    forte = request.json.get('forte')
    description = request.json.get('description')
    image = request.json.get('image')
    if barbername is None or phonenumber is None or forte is None or description is None or image is None:
        abort(400)  # missing arguments

    barbers = Barber.query.filter_by(hide=False).all()

    destination_path = 'D:/TMAIntern/Project/FrontEnd/bookingbarber/src/assets/barberImages/barber'+str(len(barbers)+1)+'.jpg'  # Đường dẫn đến vị trí lưu hình ảnh mới

    try:
        shutil.copyfile(image, destination_path)
        return 'Image copied successfully'
    except FileNotFoundError:
        return 'Source image not found'
    except Exception as e:
        return str(e)

    newbarber = Barber(
        barbername=barbername,
        birthday=birthday,
        phonenumber=phonenumber,
        address=address,
        forte=forte,
        description=description,
        image='barber'+str(len(barbers)+1)+'.jpg'
    )

    db.session.add(newbarber)
    db.session.commit()

    return make_response(jsonify({'message': 'Create new barber Success'}), 200)

@barber.route('/barbers/<int:id>', methods = ['PUT'])
@cross_origin(supports_credentials=True)
@jwt_required()
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
    try:
        os.remove('D:/TMAIntern/Project/FrontEnd/bookingbarber/src/assets/barberImages/barber'+barber.image+'.jpg')
        print(f"File has been deleted successfully.")
    except OSError as e:
        print(f"Error occurred while deleting file: {e}")
    barber.hide = True

    db.session.commit()

    return make_response(jsonify({'message': 'Delete success'}))