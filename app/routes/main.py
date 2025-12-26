# app/routes/main.py
from flask import Blueprint, render_template

bp_main = Blueprint('main', __name__)

@bp_main.route('/')
@bp_main.route('/taigi_game')
def entrance():
    return render_template('entrance.html')