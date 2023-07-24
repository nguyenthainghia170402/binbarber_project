from flask import Blueprint

customerimage = Blueprint('customerimage', __name__)

from . import views

