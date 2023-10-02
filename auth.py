from flask import Blueprint, render_template
from flask_login import current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET'])
def login():
    return render_template('login.html', user=current_user)

@auth.route('/logout', methods=['GET'])
def login():
    return render_template('logout.html', user=current_user)

@auth.route('/sign-up', methods=['GET'])
def login():
    return render_template('sign_up.html', user=current_user)
