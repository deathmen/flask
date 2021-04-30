# 从app模块中即从__init__.py中导入创建的app应用
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from app.models import User, Sb ,Sbhis
from app import app
from flask import request
from werkzeug.urls import url_parse
# 导入表单处理方法
from app.forms import LoginForm
from flask_login import login_required
from app import db
from app.forms import RegistrationForm
from datetime import datetime
from app.forms import EditProfileForm
import time

# 查询水表
@app.route('/sb')
def get_sb():
    list= Sb.query.all()
    sbs=[]
    for sb in list:
        dict = {}
        dict['userNo'] = sb.userNo
        dict['sAddr'] = sb.sAddr
        dict['deviceNo'] = sb.deviceNo
        dict['username'] = sb.username
        dict['sbid'] = sb.sbid
        sbhis = Sbhis.query.filter_by(sbid=sb.sbid).order_by(Sbhis.id.desc()).first()
        if not sbhis:
            dict['remark'] = ''
            dict['date'] = ''
        else:
            dict['remark'] = sbhis.remark
            dict['date'] = sbhis.date
        sbs.append(dict)
    return render_template('get_sb.html', sbs=sbs)


# 查询水表历史
@app.route('/sb/his/<int:id>')
def get_sbhis(id):
    sb = Sb.query.filter_by(sbid=id).first()
    # return sb.username
    return render_template('get_sbhis.html', sb=sb)


# 增加水表信息
@app.route('/sb/his/add', methods=['GET', 'POST'])
def add_sbhis():
    if request.method == "POST":
        if request.form["submit"] == "添加":
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            id=request.form["sbid"]
            sbhis=Sbhis(sbid=id, remark=request.form["remark"], date=date )
            add_data(sbhis)
    return redirect('/sb/his/'+id)


def add_data(obj):
    try:
        db.session.add(obj)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        flash("添加失败")


# 增加水表信息
@app.route('/sb/create', methods=['GET', 'POST'])
def create_sb():
    if request.method == "GET":
        return render_template('create_sb.html')
    else:
        username = request.form["username"]
        userno = request.form["userNo"]
        deviceno = request.form["deviceNo"]
        saddr = request.form["sAddr"]
        sb = Sb(username=username, userNo=userno, deviceNo=deviceno, sAddr=saddr)
        db.session.add(sb)
        db.session.commit()
        return redirect(url_for('index'))


# 修改水表信息
@app.route('/sb/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sb(id):
    if request.method == "GET":
        sb = Sb.query.filter_by(sbid=id).first()
        return render_template('edit_sb.html', sb=sb)
    else:
        if request.form["submit"] == "删除":
            sb = Sb.query.get(id)
            if not sb:
                flash("水表不存在")
            else:
                try:
                    db.session.delete(sb)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    db.session.rollback()
            return redirect('/sb')

        if request.form["submit"] == "修改":
            username = request.form["username"]
            userno = request.form["userNo"]
            deviceno = request.form["deviceNo"]
            saddr = request.form["sAddr"]
            if not username:
                flash("请输入修改后的人名")
                return redirect('/')
            sb = Sb.query.get(id)
            if not sb:
                flash("人名不存在")
            else:
                sb.username = username
                sb.userNo = userno
                sb.deviceNo = deviceno
                sb.sAddr = saddr
                try:
                    db.session.merge(sb)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    db.session.rollback()
            return redirect(url_for('get_sb'))


# 建立路由，通过路由可以执行其覆盖的方法，可以多个路由指向同一个方法。
@app.route('/')
@app.route('/index')
@login_required
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    # 对表格数据进行验证
    if form.validate_on_submit():
        # 根据表格里的数据进行查询，如果查询到数据返回User对象，否则返回None
        user = User.query.filter_by(username=form.username.data).first()
        # 判断用户不存在或者密码不正确
        if user is None or not user.check_password(form.password.data):
            # 如果用户不存在或者密码不正确就会闪现这条信息
            flash('无效的用户名或密码')
            # 然后重定向到登录页面
            return redirect(url_for('login'))
        # 这是一个非常方便的方法，当用户名和密码都正确时来解决记住用户是否记住登录状态的问题
        login_user(user, remember=form.remember_me.data)
        # 此时的next_page记录的是跳转至登录页面是的地址
        next_page = request.args.get('next')
        # 如果next_page记录的地址不存在那么就返回首页
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        # 综上，登录后要么重定向至跳转前的页面，要么跳转至首页
        return redirect(next_page)
    return render_template('login.html', title='登录', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜你成为我们网站的新用户!')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username):
    users = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': users, 'body': '测试Post #1号'},
        {'author': users, 'body': '测试Post #2号'}
    ]

    return render_template('user.html', user=users, posts=posts)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# 编辑个人资料
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('你的提交已变更.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='个人资料编辑', form=form)
