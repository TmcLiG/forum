import uuid
from flask import session, url_for, render_template, request, abort
from functools import wraps

from models.user import User


def current_user():
    uid = session.get('user_id', '')
    u = User.one(id=uid)
    return u

def login_required(routes_function):
    @wraps(routes_function)
    def f():
        print('login_required,111')
        u = current_user()
        if u is None:
            print('重新登陆')
            return render_template('index.html')
        else:
            print('登录用户', u, routes_function)
            return routes_function()

    return f

def login_required_id(routes_function):
    @wraps(routes_function)
    def f(*args, **kwargs):
        print('login_required,111')
        u = current_user()
        if u is None or u.id is not kwargs['id']:
            print('重新登陆')
            return render_template('index.html')
        else:
            print('登录用户', u, routes_function)
            return routes_function(*args, **kwargs)

    return f

csrf_tokens = dict()
def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    csrf_tokens[token] = u.id
    return token

def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']

        u = current_user()
        if token in csrf_tokens and csrf_tokens[token] == u.id:
            csrf_tokens.pop(token)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper
