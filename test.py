# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>hello world</h1>'


@app.route('/hello/<name>')
@app.route('/hello')
def hello(name=None):
    if name is not None:
        pass
    else:
        name = "World"

    return 'Hello %s ' % name


@app.route('/user/<int:user_id>')
def get_user(user_id):
    return 'User ID: %d' % user_id


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
