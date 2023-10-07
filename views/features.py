from flask import Blueprint, request, redirect, json, current_app, jsonify, flash, url_for
from flask_login import current_user, login_required
from pywebpush import webpush, WebPushException
from .models import User, Subscription
from . import db

features = Blueprint('features', __name__)

@features.route('/notify', methods=['GET'])
@login_required
def home():
    subject = 'subject'
    body = 'body'
    subscription = Subscription.query.filter_by(user_id=current_user.id).first()
    if subscription:
        push_notification(subject, body, subscription)
    else:
        flash('Subscribe for notifications in order to obtain a notification', category='error')
        
    return redirect(url_for('views.home'))
    
    
   
@features.route("/api/push-subscriptions", methods=["POST"])
@login_required
def create_push_subscription():
    print("called")
    json_data = request.get_json()
    subscription = Subscription.query.filter_by(
        user_id=current_user.id
    ).first()
    if subscription is None:
        subscription = Subscription(
            subscription_data=json_data['subscription_json'],
            user_id=current_user.id
        )
        db.session.add(subscription)
        db.session.commit()
    return jsonify({
        "status": "success"
    })
    
    
def push_notification(subject, body, push_subscription):
    try:
        response = webpush(
            subscription_info=json.loads(push_subscription.subscription_data),
            data=json.dumps({"title": subject, "body": body}),
            vapid_private_key=current_app.config['VAPID_PRIVATE_KEY'],
            vapid_claims={"sub": "mailto:webpush@mydomain.com"}
        )
        return response.ok
    except WebPushException as ex:
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message
                  )
        return False
