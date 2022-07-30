from app.auth import bp_auth
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from flask import render_template, redirect, url_for, flash, request, session, Response
from app import db
from app.models import User, Chats
from app.auth.forms import RegistrationForm, LoginForm


@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp_auth.route('/quick_login', methods=['POST'])
def quick_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    name = request.form.get('username')
    password=request.form.get('password')
    user = User.query.filter_by(username=name).first()
    if user is None or not user.check_password(password):
        flash('Invalid username or password')
        return redirect(url_for('auth.login'))
    login_user(user)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('main.index')
    return redirect(next_page)

@bp_auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp_auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register',
                           form=form)