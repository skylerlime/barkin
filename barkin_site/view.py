from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from functools import wraps
from werkzeug.exceptions import abort

from barkin_site.db import get_db

bp = Blueprint('view', __name__)

def is_logged_in():
    return 'user_id' in session

def get_logged_in_user():
    return session.get('user_id')

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not is_logged_in():
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    logged_in = is_logged_in()

    if request.method == 'POST' and logged_in:
        event_name = request.form.get('EventName')
        event_org = request.form.get('EventOrganization')

        if event_name and event_org:
            user_id = session['user_id']

            saved_row = db.execute(
                "SELECT 1 FROM SavedEvents WHERE UserID = ? AND EventName = ? AND EventOrganization = ?",
                (user_id, event_name, event_org)
            ).fetchone()

            if saved_row:
                db.execute(
                    "DELETE FROM SavedEvents WHERE UserID = ? AND EventName = ? AND EventOrganization = ?",
                    (user_id, event_name, event_org)
                )
            else:
                db.execute(
                    "INSERT INTO SavedEvents (UserID, EventName, EventOrganization) VALUES (?, ?, ?)",
                    (user_id, event_name, event_org)
                )
            db.commit()

        return redirect(url_for('index'))

    search = request.args.get('search', '').strip()
    medium = request.args.get('medium', '')
    duration = request.args.get('duration', '')
    skilllevel = request.args.get('skilllevel', '')
    cost = request.args.get('cost', '')

    query = '''
        SELECT Review.*, Event.Medium, Event.AverageRating, Event.Info
        FROM Review
        JOIN Event ON Review.EventName = Event.Name AND Review.EventOrganization = Event.Organization
        WHERE Review.ID = (
            SELECT ID FROM Review AS R2
            WHERE R2.EventName = Review.EventName AND R2.EventOrganization = Review.EventOrganization
            ORDER BY R2.PublishedAt DESC, R2.ID DESC
            LIMIT 1
        )
    '''

    filters = []
    params = []

    if search:
        filters.append("Event.Name LIKE ?")
        params.append(f"%{search}%")
    if medium:
        filters.append("Event.Medium = ?")
        params.append(medium)
    if duration:
        filters.append("Event.Duration = ?")
        params.append(duration)
    if skilllevel:
        filters.append("Event.SkillLevel = ?")
        params.append(skilllevel)
    if cost == '0':
        filters.append("Event.Cost = 0")
    elif cost == '1':
        filters.append("Event.Cost != 0")

    if filters:
        query += " AND " + " AND ".join(filters)

    query += " ORDER BY Event.Name ASC, Event.Organization ASC"

    reviews = db.execute(query, params).fetchall()

    saved = set()
    if logged_in:
        rows = db.execute(
            "SELECT EventName, EventOrganization FROM SavedEvents WHERE UserID = ?",
            (session['user_id'],)
        ).fetchall()
        saved = {(row['EventName'], row['EventOrganization']) for row in rows}

    return render_template('view/index.html', reviews=reviews, logged_in=logged_in, saved=saved)


@bp.route('/event/<organization>/<name>', methods=['GET', 'POST'])
def event_detail(name, organization):
    if request.method == 'POST' and 'Return' in request.form:
        return redirect(url_for('view.index'))

    db = get_db()
    event = db.execute('SELECT * FROM Event WHERE Name = ? AND Organization = ?', (name, organization)).fetchone()
    reviews = db.execute('SELECT * FROM Review WHERE EventName = ? AND EventOrganization = ? ORDER BY PublishedAt DESC', (name, organization)).fetchall()
    return render_template('view/event_detail.html', event=event, reviews=reviews, logged_in=is_logged_in())

@bp.route('/reviewform', methods=['GET', 'POST'])
@login_required
def reviewform():
    db = get_db()
    events = db.execute('SELECT Name, Organization FROM Event ORDER BY Name ASC').fetchall()

    if request.method == 'POST':
        if 'Cancel' in request.form:
            return redirect(url_for('view.index'))
        if 'AddEvent' in request.form:
            return redirect(url_for('view.reviewform_newevent'))

        full_name = request.form.get('EventName')
        if not full_name:
            flash("Please select an event.")
            return render_template('view/reviewform.html', events=events, logged_in=True)

        name, org = full_name.split(" - ", 1)
        rating = request.form.get('rating')
        comments = request.form.get('Comments')

        if not rating or not comments:
            flash('Rating and comment are required.')
            return render_template('view/reviewform.html', events=events, logged_in=True)

        user_id = get_logged_in_user()
        db.execute(
            "INSERT INTO Review (UserID, EventName, EventOrganization, Rating, Comments) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, org, int(rating), comments)
        )
        db.commit()
        return redirect(url_for('view.index'))

    return render_template("view/reviewform.html", events=events, logged_in=True)

@bp.route('/reviewform_newevent', methods=['GET', 'POST'])
@login_required
def reviewform_newevent():
    db = get_db()

    if request.method == 'POST':
        if 'Cancel' in request.form:
            return redirect(url_for('view.index'))

        fields = [
            'EventName', 'Organization', 'rating', 'SkillLevel', 'Cost',
            'Duration', 'Medium', 'Info', 'Comments', 'Tags'
        ]
        missing = [f for f in fields if not request.form.get(f)]
        if missing:
            flash(f"Missing fields: {', '.join(missing)}")
            return render_template('view/reviewform_newevent.html', logged_in=True)

        user_id = get_logged_in_user()
        db.execute(
            "INSERT INTO Event (Name, Organization, Medium, Duration, SkillLevel, Info, Tags, Cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (request.form['EventName'], request.form['Organization'], request.form['Medium'],
             request.form['Duration'], request.form['SkillLevel'], request.form['Info'],
             request.form['Tags'], request.form['Cost'])
        )
        db.execute(
            "INSERT INTO Review (UserID, EventName, EventOrganization, Rating, Comments) VALUES (?, ?, ?, ?, ?)",
            (user_id, request.form['EventName'], request.form['Organization'], int(request.form['rating']), request.form['Comments'])
        )
        db.commit()
        return redirect(url_for('view.index'))

    return render_template("view/reviewform_newevent.html", logged_in=True)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = get_db()
    user_id = get_logged_in_user()

    if request.method == 'POST' and 'remove' in request.form:
        event_name = request.form['EventName']
        event_org = request.form['EventOrganization']

        cursor = db.execute(
            "DELETE FROM SavedEvents WHERE UserID = ? AND EventName = ? AND EventOrganization = ?",
            (user_id, event_name, event_org)
        )
        if cursor.rowcount:
            db.commit()
            flash(f"Removed saved event: {event_name} - {event_org}")

    saved_events = db.execute(
        '''
        SELECT SavedEvents.UserID, SavedEvents.EventName, SavedEvents.EventOrganization, Event.Info
        FROM SavedEvents
        JOIN Event ON SavedEvents.EventName = Event.Name AND SavedEvents.EventOrganization = Event.Organization
        WHERE SavedEvents.UserID = ?
        ORDER BY SavedEvents.EventName ASC
        ''',
        (user_id,)
    ).fetchall()

    user_reviews = db.execute(
        "SELECT * FROM Review WHERE UserID = ? ORDER BY PublishedAt DESC",
        (user_id,)
    ).fetchall()

    return render_template("view/profile.html", saved_events=saved_events, user_reviews=user_reviews, logged_in=True)
