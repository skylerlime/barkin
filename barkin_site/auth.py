import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from barkin_site.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    logged_in = 'user_id' in session
    if logged_in == True:
        return redirect(url_for("index"))
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO User (Type, Email, Password) VALUES (?, ?, ?)",
                    ('User', email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Account with email {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    logged_in = 'user_id' in session
    if logged_in == True:
        return redirect(url_for("index"))
    elif request.method == 'POST':
        if 'CreateAccount' in request.form:
            return redirect(url_for('auth.register'))

        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM User WHERE Email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['Password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['ID']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logged_in = 'user_id' in session
    if logged_in == False:
        return redirect(url_for("index"))
    session.clear()
    return redirect(url_for('index'))