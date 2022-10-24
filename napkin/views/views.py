import sys
from flask import Blueprint, request, jsonify, redirect, session, g, render_template, url_for
import json
import os
from bson.objectid import ObjectId
import bcrypt 
from datetime import date
from napkin.api.models import Users as Users
from database import database
from napkin.utils import login_required

views = Blueprint('views', __name__, template_folder="templates", static_folder="static")
users = Users(database)
urls = database.urls

@views.context_processor
def inject_context():
    host_url = os.environ.get('HOST_URL')
    if 'user' in session.keys() and users.users.find_one({'_id': ObjectId(session['user'])}):
            current_user = users.users.find_one({'_id': ObjectId(session['user'])})
            return dict(current_user=current_user, host_url=host_url)
    else:
        return dict(no_session=True, host_url=host_url)

# User registration 
@views.route("/", methods=['GET'])
def landing_page():
    if 'user' in session.keys() and users.users.find_one({'_id': ObjectId(session['user'])}):
        return redirect('/urls')
    return render_template('landing.html')

# User registration 
@views.route("/register", methods=['GET'])
def register():
    if 'user' in session.keys() and users.users.find_one({'_id': ObjectId(session['user'])}):
        return redirect('/urls')
    else:
        return render_template('auth/register.html')

@views.route('/login', methods=['GET'])
def login():
    if 'user' in session.keys() and users.users.find_one({'_id': ObjectId(session['user'])}):
        return redirect('/urls')
    return render_template('/auth/login.html')

# Index view         
@views.route("/urls")
@login_required()
def list_view():
    all_urls = list(urls.find({'owner': session['user']}))
    return render_template('urls.html', urls=all_urls, user=session['user'])

@views.route('/r/<alias>')
def route_alias(alias):
    url = list(urls.find({'alias': alias}))
    if url:
        alias = url[0]['destination']
        return render_template('redirect.html', alias=alias)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('FLASK_RUN_PORT'))

    




