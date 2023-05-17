import sys
import json

from flask import jsonify, request, session, abort, make_response
from flask_login import current_user, login_required
from datetime import datetime, timedelta



from . import booking

from .. import db
from ..models import Service, Booking, Customer, Barber, WorkTime

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.isadmin:
        abort(403)

#_____________API FOR ADMIN AND CLIENT___________
#Add new booking
@booking.route('/booking', methods=['POST'])
@login_required
def add_new_booking():
    bookingdate = request.json.get('bookingdate')
    bookingtime = request.json.get('bookingtime')
    customerid = request.json.get('customerid')
    barberid = request.json.get('barberid')
    serviceids = request.json.get('services')
    state = "Wait for confirmation"

    customer = Customer.query.filter_by(customerid=customerid, hide=False).first_or_404()
    barber = Barber.query.filter_by(barberid=barberid, hide=False).first_or_404()

    newBooking = Booking(
        bookingdate = bookingdate,
        bookingtime = bookingtime,
        state = state,
        barber = barber,
        customer = customer
    )

    timeAdd = 0

    for serviceid in serviceids:
        service = Service.query.filter_by(serviceid=serviceid, hide=False).first_or_404()
        newBooking.booked_services.append(service)
        timeAdd += service.timeofservice

    timeFrom = datetime.strptime(bookingtime, '%Y-%m-%d %H:%M:%S')
    timeChange = timedelta(minutes=timeAdd)
    timeTo = timeFrom + timeChange
    #formatted timeTo
    #timeTo.strftime("%Y-%m-%d %H:%M:%S")

    #handle worktime's barber
    newWorktime = WorkTime(
        date=timeFrom.strftime("%Y-%m-%d"),
        timefrom=timeFrom.strftime("%H:%M:%S"),
        timeto=timeTo.strftime("%H:%M:%S"),
        statework="Wait for confirmation ",
        barberWTime=barber
    )

    #Debug---
    #return make_response(jsonify({'message': newWorktime.barberWTime.barbername}), 200)
    #return make_response(jsonify({'message': timeTo.strftime("%Y-%m-%d %H:%M:%S")}), 200)
    # Debug---

    db.session.add_all([newBooking, newWorktime])
    db.session.commit()

    return make_response(jsonify({'message': 'Add new booking Success'}), 200)

#Get Booking detail by id
@booking.route('/booking/<int:id>', methods=['GET'])
@login_required
def get_booking_by_id(id):
    booking = Booking.query.filter_by(bookingid=id, hide=False).first_or_404()
    if not booking:
        return make_response(jsonify({'message': 'Booking is empty'}), 404)
    customer = Customer.query.filter_by(customerid=booking.customerid, hide=False).first_or_404()
    barber = Barber.query.filter_by(barberid=booking.barberid, hide=False).first_or_404()
    worktime = WorkTime.query.filter_by(barberid=barber.barberid, date=booking.bookingdate, timefrom=booking.bookingtime).first_or_404()
    servicesList = []
    for service in booking.booked_services:
        serviceDict = {
            "serviceid": service.serviceid,
            "servicename": service.servicename,
            "timeofservice": service.timeofservice,
            "price": service.price,
            "createat": service.createat
        }
        servicesList.append(serviceDict)
        if not servicesList:
            return make_response(jsonify({'message': 'Services is empty'}), 404)

    return make_response(jsonify({
        "bookingid": booking.bookingid,
        "customer": {
            "customerid": customer.customerid,
            "customername": customer.customername
        },
        "barber": {
            "barberid": barber.barberid,
            "barbername": barber.barbername
        },
        "worktimeid": worktime.worktimeid,
        "services": servicesList,
        "bookingdate": booking.bookingdate.strftime("%Y-%m-%d"),
        "bookingtime": booking.bookingtime.strftime("%H:%M:%S"),
        "state": booking.state,
        "createat": booking.createat
    }))

#Edit booking
@booking.route('/booking/<int:id>', methods=['PUT'])
@login_required
def edit_booking(id):
    booking = Booking.query.filter_by(bookingid=id, hide=False).first_or_404()
    if not booking:
        return make_response(jsonify({'message': 'Booking is empty'}), 404)
    bookingdate = request.json.get('bookingdate')
    bookingtime = request.json.get('bookingtime')
    customerid = request.json.get('customerid')
    oldbarberid = request.json.get('oldbarberid')
    newbarberid = request.json.get('newbarberid')
    worktimeid = request.json.get('worktimeid')
    serviceids = request.json.get('services')

    customer = Customer.query.filter_by(customerid=customerid, hide=False).first_or_404()
    barber = Barber.query.filter_by(barberid=newbarberid, hide=False).first_or_404()

    booking.bookingdate = bookingdate
    booking.bookingtime = bookingtime
    # booking.customer = customer
    booking.barber = barber


    # Handle service of booking
    # for oldService in booking.booked_services:
    #     booking.booked_services.remove(oldService)
    #remove all old services of booking
    booking.booked_services = []
    timeAdd = 0

    for serviceid in serviceids:
        service = Service.query.filter_by(serviceid=serviceid, hide=False).first_or_404()
        booking.booked_services.append(service)
        timeAdd += service.timeofservice
    servicesList = []
    for service in booking.booked_services:
        serviceDict = {
            "serviceid": service.serviceid,
            "servicename": service.servicename,
            "timeofservice": service.timeofservice,
            "price": service.price,
            "createat": service.createat
        }
        servicesList.append(serviceDict)
    if not servicesList:
        return make_response(jsonify({'message': 'Services is empty'}), 404)

    timeFrom = datetime.strptime(bookingtime, '%H:%M:%S')
    timeChange = timedelta(minutes=timeAdd)
    timeTo = timeFrom + timeChange
    # formatted timeTo
    # timeTo.strftime("%Y-%m-%d %H:%M:%S")

    # handle worktime's barber
    if oldbarberid == newbarberid:
        for worktime in barber.worktimes:
            if worktime.worktimeid == worktimeid:
                worktime.date = bookingdate
                worktime.timefrom = timeFrom
                worktime.timeto = timeTo
                worktime.barberWTime = barber
    else:
        oldbarber = Barber.query.filter_by(barberid=oldbarberid, hide=False).first_or_404()
        for worktime in oldbarber.worktimes:
            if worktime.worktimeid == worktimeid:
                db.session.delete(worktime)

        newWorktime = WorkTime(
            date=bookingdate,
            timefrom=timeFrom,
            timeto=timeTo,
            statework="Wait for confirmation ",
            barberWTime=barber
        )
        db.session.add(newWorktime)

            #debug_____
            #return make_response(jsonify({'message': worktime.timeto.strftime("%H:%M:%S")}), 200)

    # Update worktime by delete old create new
    # db.session.delete(barber.worktimes[0])
    # newWorktime = WorkTime(
    #     date=bookingdate,
    #     timefrom=timeFrom,
    #     timeto=timeTo,
    #     statework="Wait for confirmation ",
    #     barberWTime=barber
    # )
    # db.session.add(newWorktime)
    # Debug---
    # return make_response(jsonify({'message': newWorktime.barberWTime.barbername}), 200)
    # return make_response(jsonify({'message': timeTo.strftime("%H:%M:%S")}), 200)
    # Debug---


    db.session.commit()

    return make_response(jsonify({
            "bookingid": booking.bookingid,
            "customer": {
                "customerid": customer.customerid,
                "customername": customer.customername
            },
            "barber": {
                "barberid": barber.barberid,
                "barbername": barber.barbername
            },
            "worktimeid": worktimeid,
            "services": servicesList,
            "bookingdate": booking.bookingdate.strftime("%Y-%m-%d"),
            "bookingtime": booking.bookingtime.strftime("%H:%M:%S"),
            "state": booking.state,
            "createat": booking.createat
        }), 200)

#_____________API FOR ADMIN AND CLIENT___________


#_____________API FOR ADMIN____________
##Get list booking filter by date
@booking.route('/admin/booking', methods=['POST'])
@login_required
def get_list_booking_by_date():
    check_admin()
    bookingdate = request.json.get('bookingdate')
    bookings = Booking.query.filter_by(bookingdate=bookingdate, hide=False).all()
    if not bookings:
        return make_response(jsonify({'message': 'Bookings is empty'}), 404)
    bookingsList = []

    for booking in bookings:
        customer = Customer.query.filter_by(customerid=booking.customerid, hide=False).first_or_404()
        barber = Barber.query.filter_by(barberid=booking.barberid, hide=False).first_or_404()
        worktime = WorkTime.query.filter_by(barberid=barber.barberid, date=bookingdate, timefrom=booking.bookingtime).first_or_404()
        servicesList = []
        for service in booking.booked_services:
            serviceDict = {
                "servicename": service.servicename,
                "timeofservice": service.timeofservice,
                "price": service.price,
                "createat": service.createat
            }
            servicesList.append(serviceDict)
            if not servicesList:
                return make_response(jsonify({'message': 'Services is empty'}), 404)
        bookingDict = {
            "bookingid": booking.bookingid,
            "customer": {
                    "customerid": customer.customerid,
                    "customername": customer.customername
                }
            ,
            "barber": {
                    "barberid": barber.barberid,
                    "barbername": barber.barbername
                }
            ,
            "worktimeid": worktime.worktimeid,
            "services": servicesList,
            "bookingdate": booking.bookingdate.strftime("%Y-%m-%d"),
            "bookingtime": booking.bookingtime.strftime("%H:%M:%S"),
            "state": booking.state,
            "createat": booking.createat
        }
        bookingsList.append(bookingDict)
    if not bookingsList:
        return make_response(jsonify({'message': 'Services is empty'}), 404)

    return make_response(jsonify({'bookings': bookingsList}), 200)

##Confirm booking
@booking.route('/admin/booking/<int:id>', methods=['PUT'])
@login_required
def confirm_booking(id):
    check_admin()
    booking = Booking.query.filter_by(bookingid=id, hide=False).first_or_404()
    if not booking:
        return make_response(jsonify({'message': 'Booking is empty'}), 404)

    worktimeid = request.json.get('worktimeid')
    worktime = WorkTime.query.filter_by(worktimeid=worktimeid).first_or_404()

    booking.state = "Confirmed"
    worktime.statework = "Working"

    db.session.commit()
    return make_response(jsonify({'message': 'Confirm success'}), 200)

##Cancel booking
@booking.route('/admin/booking/<int:id>', methods=['DELETE'])
@login_required
def cancel_booking(id):
    check_admin()
    booking = Booking.query.filter_by(bookingid=id, hide=False).first_or_404()
    if not booking:
        return make_response(jsonify({'message': 'Booking is empty'}), 404)

    worktimeid = request.json.get('worktimeid')
    worktime = WorkTime.query.filter_by(worktimeid=worktimeid).first_or_404()

    booking.hide = True

    db.session.delete(worktime)
    db.session.commit()
    return make_response(jsonify({'message': 'Cancel success'}), 200)

#_____________API FOR ADMIN____________


#_____________API FOR CLIENT___________



#_____________API FOR CLIENT___________
