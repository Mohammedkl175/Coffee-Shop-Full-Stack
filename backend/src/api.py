import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES
'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['GET'])
def get_drinks():
    try:
        Drinks = Drink.query.all()
        drinks = [drink.short() for drink in Drinks]
        return jsonify({'success':True,
        'drinks':drinks})
    except:
        abort(422)

'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        Drinks = Drink.query.all()
        drinks = [drink.long() for drink in Drinks]
        return jsonify({'success':True,
        'drinks':drinks})
    except:
        abort(422)

'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    try:
        body = request.get_json()
        title = body.get('title',None)
        recipe = body.get('recipe',None)
        if body is None:
            abort(405)
        elif title is None or recipe is None:
            abort(405)
        else:
            new_drink = Drink()
            new_drink.title = title
            new_drink.recipe = json.dumps(recipe)
            new_drink.insert()
            drink = new_drink.long()
            return jsonify({'success':True,
            'drinks':drink})
    except:
        abort(422)

'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(id):
    drink_to_update = Drink.query.get(id)
    body = request.get_json()
    title = body.get('title',None)
    recipe = body.get('recipe',None)
    if drink_to_update is None:
        abort(404)
    else:
        if title is not None:
            drink_to_update.title = title
        if recipe is not None:
            drink_to_update.recipe = json.dumps(recipe)
        drink_to_update.update()
        drink = drink_to_update.long()
        return jsonify({'success':True,
        'drinks':drink})

'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id):
    try:
        drink_to_delete = Drink.query.get(id)
        if drink_to_delete is None:
            abort(404)
        else :
            drink_to_delete.delete()
            return jsonify({'success':True,
            'delete':id})
    except:
        abort(422)

## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "Resource Not Found"
        }), 404

@app.errorhandler(405)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': "Method Not Allowed"
        }), 405

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad Request"
        }), 400

@app.errorhandler(401)
def Unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': "Unauthorized"
        }), 400
