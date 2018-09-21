import uuid
import os
import hashlib
from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
)

from models.user import User
from models.topic import Topic
from models.reply import Reply
from routes import login_required, login_required_id
from utils import log


main = Blueprint('index', __name__)


def current_user():
    # 从 session 中找到 user_id 字段, 找不到就 -1
    # 然后用 id 找用户
    # 找不到就返回 None
    uid = session.get('user_id', -1)
    u = User.one(id=uid)
    return u

def hash_pass(password, salt='$!@><?>HUI&DWQa`'):
    str = hashlib.sha256(password.encode('ascii')).hexdigest()
    s = str + salt
    result = hashlib.sha256(s.encode('ascii')).hexdigest()
    return  result


"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    # form = request.args
    form = request.form
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    print('login user <{}>'.format(u))
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('.index'))
    else:
        # session 中写入 user_id
        session['user_id'] = u.id
        print('session是什么：', session)
        # 设置 cookie 有效期为 永久
        session.permanent = True
        return redirect(url_for('gua_topic.index'))


@main.route('/profile')
@login_required
def profile():
    u = current_user()
    t = Topic.all(user_id=u.id)
    t.reverse()
    r = Reply.all(user_id=u.id)
    r.reverse()
    print('t是什么：', t)
    print('r是什么:', r)
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template('profile.html', user=u, topic=t, reply=r)


@main.route('/user/<int:id>')
@login_required_id
def user_set(*args, **kwargs):
    id = kwargs['id']
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('set.html', user=u)

@main.route('/user/update', methods=['POST'])
def user_update():
    u = current_user()
    form = request.form.to_dict()
    print('form:', form, u)
    if 'old_pass' in form and u.password == hash_pass(form['old_pass']):
        form.pop('old_pass')
        form['password'] = hash_pass(form['password'])
        User.update(u.id, **form)
    else:
        User.update(u.id, **form)
    return redirect(url_for('.user_set', id=u.id))


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file = request.files['avatar']
    # ../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    path = os.path.join('images', filename)
    file.save(path)

    u = current_user()
    User.update(u.id, image='/images/{}'.format(filename))

    return redirect(url_for('.profile'))

@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:2000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    return send_from_directory('images', filename)


def not_found(e):
    return render_template('404.html')


# def blueprint():
#     main = Blueprint('index', __name__)
#     main.route("/")(index)
#     main.route("/register", methods=['POST'])(register)
#     main.route("/login", methods=['POST'])(login)
#     main.route('/profile')(profile)
#     main.route('/user/<int:id>')(user_detail)
#
#     return main
