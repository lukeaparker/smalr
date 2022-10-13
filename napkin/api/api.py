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
        return redirect('/napkins')
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
    new_napkin = urls.insert_one({
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
    if 'canvas' in request.form.keys():
        canvas = json.loads(request.form['canvas'])
        napkin = napkins.update_one({'_id': ObjectId(_id)}, {'$set': {'canvas': canvas}})
        return 'success'
    if 'title' in request.form.keys():
        title = request.form['title']
        napkin = napkins.update_one({'_id': ObjectId(_id)}, {'$set': {'title': title}})
        return redirect(f'/napkin/{_id}')

# Delete napkin
@api.route("/delete/<_id>", methods=['GET'])
@login_required()
def delete_url(_id):
        napkin = urls.delete_one({'_id': ObjectId(_id)})
        return redirect('/urls')

