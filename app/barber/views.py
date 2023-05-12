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

    for barber in barbers:
        customerDict = {
            "barberid" : barber.customerid,
            "barbername" : barber.customername,
            "phonenumber" : barber.phonenumber,
            "address" : barber.address,
            "birthday": barber.birthday,
            "forte": barber.forte,
            "description": barber.description,
            "image": barber.image,
            "createat" : barber.createat
        }
        barbersList.append(customerDict)

    return jsonify({'customers' : barbersList})

