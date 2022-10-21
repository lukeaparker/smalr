import sys
from flask import Blueprint, request, jsonify, redirect, session, g, render_template
import json
import os
from bson.objectid import ObjectId
import bcrypt 
from datetime import date
from napkin.api.models import Users as Users
from database import database
from napkin.utils import login_required

api = Blueprint('api', __name__)
users = Users(database)
urls = database.urls

@api.route('/register', methods=['POST'])
def register():
    user = {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'email': request.form.get('email'),
        'password': bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()),
    }
    users.create_user(user)
    return redirect('/login')

@api.route('/login', methods=['POST'])
def login():
    user = users.verify_credentials({
        'email': request.form.get('email'),
        'password': request.form.get('password').encode('utf-8'),
    })
    if user != False:
        session['user'] = str(user['_id'])
        return redirect('/urls')
    else: 
        return redirect('/login')

@api.route('/logout')
def logout():
    session['user'] = None 
    return redirect('/')

# Create napkin 
@api.route("/create", methods=['POST'])
@login_required()
def create():
    urls.insert_one({
        'name': request.form['name'],
        'owner': session['user'], 
        'date_created': str(date.today()),
        'destination': request.form['destination'],
        'alias': request.form['alias']
    })
    return redirect(f'/urls')

# Update napkin 
@api.route("/update/<_id>", methods=['POST'])
@login_required()
def update_url(_id):
    updated_url = {
        'name': request.form['name'],
        'owner': session['user'], 
        'date_created': str(date.today()),
        'destination': request.form['destination'],
        'alias': request.form['alias'] 
    }
    urls.update_one({'_id': ObjectId(_id)}, {'$set': updated_url})
    return redirect(f'/urls')

# Delete napkin
@api.route("/delete/<_id>", methods=['GET'])
@login_required()
def delete_url(_id):
        napkin = urls.delete_one({'_id': ObjectId(_id)})
        return redirect('/urls')

@api.route('/validate/alias', methods=['POST'])
def validate_alias():
    alias = list(urls.find({'alias': request.form['alias']}))
    if alias:
        if request.args.get('name'):
            url = list(urls.find({'name': request.args.get('name')}))[0]
            print(url['alias'], alias[0]['alias'])
            if alias[0]['alias'] == url['alias']:
                return 'True'
        return 'False'
    else:
        return 'True'

@api.route('/validate/name', methods=['POST'])
def validate_name():
    name = request.form['name']
    url = list(urls.find({'name': name}))
    if url:
        return 'False' 
    else:
        return 'True'

