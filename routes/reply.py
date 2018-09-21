from flask import (
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import current_user

from models.reply import Reply
from models.user import User
from models.message import Messages

def users_from_content(content):
    parts = content.split()
    users = []
    for p in parts:
        if p.startswith('@'):
            username = p[1:]
            u = User.one(username=username)
            if u is not None:
                users.append(u)
    return users

def send_mails(sender, receivers, content):
    for r in receivers:
        form = dict(
            title='你被 {} AT 了'.format(sender.username),
            content=content,
            sender_id=sender.id,
            receiver_id=r.id
        )
        Messages.new(form)

main = Blueprint('gua_reply', __name__)

@main.route("/add", methods=["POST"])
def add():
    form = request.form.to_dict()
    u = current_user()

    content = form['content']
    users = users_from_content(content)
    send_mails(u, users, content)

    print('DEBUG', form)
    m = Reply.add(form, user_id=u.id)
    return redirect(url_for('gua_topic.detail', id=m.topic_id))

