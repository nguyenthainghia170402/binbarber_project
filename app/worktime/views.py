import sys
import json

from flask import jsonify, request, session, abort, make_response
from flask_login import current_user, login_required
from datetime import datetime

from . import worktime
from .. import db
from ..models import WorkTime, Barber


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.isadmin:
        abort(403)

@worktime.route('/worktime/<int:id>', methods=['POST'])
@login_required
def get_list_worktime_barber(id):
    check_admin()

    date = request.json.get('date')

    worktimes = WorkTime.query.filter_by(barberid=id, date=date)
    worktimesList = []
    for worktime in worktimes:
        worktimeDict = {
            "worktimeid": worktime.worktimeid,
            "date": worktime.date,
            "timefrom": worktime.timefrom,
            "timeto": worktime.timeto,
            "statework": worktime.statework
        }
        worktimesList.append(worktimeDict)

    if not worktimesList:
        return make_response(jsonify({'message': 'Worktimes is empty'}), 404)
    return make_response(jsonify({
        'worktimes': worktimesList,
        'barberid': id
    }))

@worktime.route('/worktime/leave/<int:id>', methods=['POST'])
@login_required
def add_leave_time_for_barber(id):
    check_admin()
    date = request.json.get('date')
    timefrom = request.json.get('timefrom')
    timeto = request.json.get('timeto')
    barber = Barber.query.filter_by(barberid=id, hide=False).first_or_404()
    newLeaveWorkTime = WorkTime(
        date=date,
        timefrom=timefrom,
        timeto=timeto,
        statework="Leaving",
        barberWTime=barber
    )

    db.session.add(newLeaveWorkTime)
    db.session.commit()

    return make_response(jsonify({'message': 'Add leave time success'}))

@worktime.route('/worktime/leave/<int:id>', methods=['PUT'])
@login_required
def edit_leave_time_of_barber(id):
    check_admin()
    date = request.json.get('date')
    timefrom = request.json.get('timefrom')
    timeto = request.json.get('timeto')
    worktime = WorkTime.query.filter_by(worktimeid=id).first_or_404()

    worktime.date = date
    worktime.timefrom = timefrom
    worktime.timeto = timeto

    db.session.commit()

    return make_response(jsonify({
        'worktime': {
            "worktimeid": worktime.worktimeid,
            "date": worktime.date.strftime("%Y-%m-%d"),
            "timefrom": worktime.timefrom.strftime("%H:%M:%S"),
            "timeto": worktime.timeto.strftime("%H:%M:%S"),
            "statework": worktime.statework
        },
        'barberid': worktime.barberid
    }))

@worktime.route('/worktime/leave/<int:id>', methods=['DELETE'])
@login_required
def cancel_leave_time_of_barber(id):
    check_admin()
    worktime = WorkTime.query.filter_by(worktimeid=id).first_or_404()
    db.session.delete(worktime)
    db.session.commit()
    return make_response(jsonify({'message':'Cancel leave time success'}))



