from flask import Blueprint

worktime = Blueprint('worktime', __name__)

from . import views

