from flask import render_template, redirect, url_for, flash, request, current_app
from urllib.parse import urlsplit # Changed import from werkzeug.urls
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = db.session.scalar(
                db.select(User).where(User.username == form.username.data))
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            # Use urlsplit to check if the next_page has a netloc (domain part)
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('main.index')
            flash(f'Welcome back, {user.username}!')
            return redirect(next_page)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during login: {e}")
            flash('An error occurred during login. Please try again.')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required # Ensure user is logged in before they can log out
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            # Log the user in automatically after registration
            login_user(user)
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during registration: {e}")
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', title='Register', form=form)
