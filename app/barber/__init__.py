from flask import Blueprint

barber = Blueprint('barber', __name__)

from . import views