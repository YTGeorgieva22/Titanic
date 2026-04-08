from flask import render_template

from main.routes import current_user
from . import auth_bp
from .forms import LoginForm, RegisterForm
from .models import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
    return render_template('login.html', form = form, current_user=current_user)

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    pass

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
    return render_template('register.html', form = form, current_user=current_user)