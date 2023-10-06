from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET'])
def login():
    return render_template('login.html', user=current_user)

@auth.route('/logout', methods=['GET'])
def logout():
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET'])
def sign_up():
    return render_template('sign_up.html', user=current_user)
