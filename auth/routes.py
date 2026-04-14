from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import LoginForm, RegisterForm
from .models import User
from __init__ import db
from flask import render_template, redirect, url_for, flash, session

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_user(current_user, remember=False)
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('main_bp.dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_user:
            flash('Username already exists.', 'warning')
            return redirect(url_for('auth.register'))

        existing_email = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_email:
            flash('Email already exists.', 'warning')
            return redirect(url_for('auth.register'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )

        db.session.add(user)
        db.session.commit()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)