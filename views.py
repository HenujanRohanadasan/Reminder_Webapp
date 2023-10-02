from flask import Blueprint, request, render_template

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def home():
    print('working')
    return render_template('home.html')
