from flask import Blueprint
bp = Blueprint('war', __name__)
from app.war import routes