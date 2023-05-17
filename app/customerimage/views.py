import sys
import json

from flask import jsonify, request, session, abort, make_response
from flask_login import current_user, login_required
from datetime import datetime

from . import customerimage
from .. import db
from ..models import CustomerImage, Barber


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.isadmin:
        abort(403)

@customerimage.route('/cusimages', methods=['GET'])
@login_required
def get_list_customer_image():
    cusimages = CustomerImage.query.all()


    cusimagesList = []

    for cusimage in cusimages:
        cusimageDict = {
            "cusimageid": cusimage.cusimageid,
            "image": cusimage.image,
            "barberid": cusimage.barberid,
            "createat": cusimage.createat
        }
        cusimagesList.append(cusimageDict)

    if not cusimagesList:
        return make_response(jsonify({'message': 'Customer Image is empty'}),404)

    return make_response(jsonify({'cusimages': cusimagesList}))

@customerimage.route('/cusimages', methods=['POST'])
@login_required
def add_new_customer_image():
    check_admin()
    image = request.json.get('image')
    barberid = request.json.get('barberid')

    barber = Barber.query.filter_by(barberid=barberid).first_or_404()

    newCusimage = CustomerImage(
        image=image,
        barberCIma=barber
    )

    db.session.add(newCusimage)
    db.session.commit()

    return make_response(jsonify({'message': 'Add new customer image success'}),200)

@customerimage.route('/cusimages/<int:id>', methods=['GET'])
@login_required
def get_customer_image_by_id(id):
    cusimage = CustomerImage.query.get_or_404(id)
    if cusimage is None:
        return make_response(jsonify({'message': 'Do not have this customer image'}), 404)
    return make_response(jsonify({
        "cusimageid": cusimage.cusimageid,
        "image": cusimage.image,
        "barberid": cusimage.barberid,
        "createat": cusimage.createat
    }))

@customerimage.route('/cusimages/<int:id>', methods=['PUT'])
@login_required
def edit_customer_image(id):
    check_admin()
    image = request.json.get('image')
    barberid = request.json.get('barberid')
    cusimage = CustomerImage.query.get_or_404(id)
    barber = Barber.query.filter_by(barberid=barberid).first_or_404()
    cusimage.image = image
    cusimage.barberCIma = barber
    db.session.commit()

    return make_response(jsonify({'message': 'Edit customer image success'}), 200)

@customerimage.route('/cusimages/<int:id>', methods=['DELETE'])
@login_required
def delete_customer_image(id):
    check_admin()
    cusimage = CustomerImage.query.get_or_404(id)
    db.session.delete(cusimage)
    db.session.commit()

    return make_response(jsonify({'message': 'Delete customer image success'}), 200)