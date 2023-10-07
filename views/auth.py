from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged In Successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('wrong password', category='error')
        else:
            flash('account does not exists', category='error')
        
    return render_template('login.html', user=current_user)

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
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
            new_user = User(email=email, user_name=user_name, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Logged In Successfully', category='success')
            return redirect(url_for('views.home'))
        
    return render_template('sign_up.html', user=current_user)
