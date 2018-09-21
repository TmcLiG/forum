from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import current_user, login_required, csrf_required, new_csrf_token

from models.topic import Topic


main = Blueprint('gua_topic', __name__)


@main.route("/")
@login_required
def index():
    u = current_user()
    print('u shenme :', u)
    ms = Topic.all()
    token = new_csrf_token()
    return render_template("topic/index.html", ms=ms, user=u, token=token)


@main.route('/<int:id>')
# /topic/1
# @main.route('/')
# /topic?id=1
def detail(id):
    # id = int(request.args['id'])
    # http://localhost:3000/topic/1
    u = current_user()
    m = Topic.get(id)

    # 不应该放在路由里面
    # m.views += 1
    # m.save()

    # 传递 topic 的所有 reply 到 页面中
    return render_template("topic/detail.html", topic=m, user=u)

@main.route("/delete")
@csrf_required
@login_required
def delete():
    id = int(request.args.get('id'))
    u = current_user()
    print('删除 topic 用户是', u, id)
    Topic.delete(id)
    return redirect(url_for('.index'))


@main.route("/add", methods=["POST"])
@csrf_required
def add():
    form = request.form.to_dict()
    u = current_user()
    m = Topic.add(form, user_id=u.id)
    return redirect(url_for('.detail', id=m.id))


@main.route("/new")
def new():
    u = current_user()
    token = new_csrf_token()
    return render_template("topic/new.html", user=u, token=token)

