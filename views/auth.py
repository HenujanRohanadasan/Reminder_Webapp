from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from . import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html', user=current_user)

@auth.route('/logout', methods=['GET'])
def logout():
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('email already exists', category='error')
        elif len(user_name) < 2:
            flash('user name is too short', category='error')
        elif len(password) < 8 or len(password) > 20:
            flash('password must contain 8-20 characters', category='error')
        elif not password == password_confirm:
            flash('passwords does not match', category='error')
        else:
            new_user = User(email=email, user_name=user_name, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Logged In Successfully', category='success')
            return redirect(url_for('views.home'))
        
    return render_template('sign_up.html', user=current_user)
