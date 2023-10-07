from flask import Blueprint, request, render_template
from flask_login import current_user, login_required

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template('home.html', user=current_user)
