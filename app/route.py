# 从app模块中即从__init__.py中导入创建的app应用
from flask import render_template

from app import app


# 建立路由，通过路由可以执行其覆盖的方法，可以多个路由指向同一个方法。
@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'duke'}
    posts = [
        {
            'author': {'username': '刘'},
            'body': '这是模板模块中的循环例子1'
        },
        {
            'author': {'username': '李'},
            'body': '这是模板模块中的循环例子2'
        }

    ]
    return render_template('index.html', title='我的', user=user, posts=posts)
