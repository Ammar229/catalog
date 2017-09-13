#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
            open('/var/www/catalog/catalog/client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('postgresql+psycopg2://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    print login_session
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('/var/www/catalog/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = \
            make_response(json.dumps('Failed to upgrade authorization code'), 
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = \
            make_response(json.dumps("Token's user ID not match given userID"), 
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = \
            make_response(json.dumps("Token's client ID not match app's"),
                          401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user already connected'),
                          200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    output += 'border-radius: 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;">'
    flash('you are now logged in as %s' % login_session['username'])
    print 'done!'
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_sessio
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = \
            make_response(json.dumps('Current user not connected.'),
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = \
            make_response(json.dumps('Failed revoke token for user',
                          400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog')
def ShowAllCategories():
    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    return render_template('categories.html', categories=categories,
                           STATE=state, logged=login_session)


@app.route('/catalog/JSON')
def ShowAllCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/items/JSON')
def ShowAllItemsJSON():
    items = session.query(Items).all()
    return jsonify(items=[i.serialize for i in items])


# Render Items in specific Category
@app.route('/catalog/<int:category_id>/items')
def showCategoryItems(category_id):
    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    category_selected = \
        session.query(Category).filter_by(id=category_id).one()
    items = \
        session.query(Items).filter_by(category_id=category_selected.id)
    return render_template(
        'categoryItems.html',
        categories=categories,
        category_selected=category_selected,
        items=items,
        STATE=state,
        logged=login_session,
        )


# Render specific Item Detalils for specific Category
@app.route('/catalog/<int:category_id>/item/<int:item_id>/details')
def showItem(category_id, item_id):
    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    category_selected = \
        session.query(Category).filter_by(id=category_id).one()
    item_selected = session.query(Items).filter_by(id=item_id).one()
    creator = getUserInfo(item_selected.user_id)
    return render_template(
        'itemDetails.html',
        category=category_selected,
        item=item_selected,
        STATE=state,
        creator=creator,
        logged=login_session,
        )


# Render form to Add Item If user login if not redirect to login page
@app.route('/catalog/<int:category_id>/add', methods=['GET', 'POST'])
def addItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Items(user_id=login_session['user_id'],
                        name=request.form['name'],
                        category_id=category.id)
        session.add(newItem)
        session.commit()
        flash('New Item has been Added')
        return redirect(url_for('showCategoryItems',
                        category_id=category.id))
    else:
        return render_template('addItem.html', category=category,
                               logged=login_session)


# Render form to Edit Item if user login and Author this Item 
@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item_selected = session.query(Items).filter_by(id=item_id).one()
    category_selected = \
        session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(item_selected.user_id)
    if login_session['user_id'] != creator.id:
        flash('not allowed edit this item add your item first to edit!')
        return redirect(url_for('showCategoryItems',
                        category_id=category_selected.id))
    if request.method == 'POST':
        item_selected.name = request.form['name']
        item_selected.description = request.form['description']
        session.add(item_selected)
        session.commit()
        flash('The Item has been Edited')
        return redirect(url_for('showCategoryItems',
                        category_id=category_selected.id))
    else:
        return render_template('editItem.html', item=item_selected,
                               category=category_selected,
                               logged=login_session)


# Render form to Delete Item if user login and Author this Item 
@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item_selected = session.query(Items).filter_by(id=item_id).one()
    category_selected = \
        session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(item_selected.user_id)
    if login_session['user_id'] != creator.id:
        flash('not allowed delete this item add your item first!')
        return redirect(url_for('showCategoryItems',
                        category_id=category_selected.id))
    if request.method == 'POST':
        session.delete(item_selected)
        session.commit()
        flash('The Item has been Deleted')
        return redirect(url_for('showCategoryItems',
                        category_id=category_selected.id))
    else:
        return render_template('deleteItem.html', item=item_selected,
                               category=category_selected,
                               logged=login_session)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

