from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user,login_user,logout_user,login_required

from myblog.forms import LoginForm
from myblog.models import Admin
from myblog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        # 先判断是否有管理员账户
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)  # 登录状态记录
                flash('Welcome back.', 'info')
                return redirect_back()
            flash('Invalid username or password.', 'warning')
        else:
            flash('No account.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required   # 登出之前保证已经登录
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()
