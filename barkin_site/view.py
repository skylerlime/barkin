from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from barkin_site.db import get_db

bp = Blueprint('view', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    logged_in = 'user_id' in session
    db = get_db()

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
    params = []

    if search:
        query += ' AND Event.Name LIKE ?'
        params.append(f'%{search}%')

    if medium:
        query += ' AND Event.Medium = ?'
        params.append(medium)

    if duration:
        query += ' AND Event.Duration = ?'
        params.append(duration)

    if skilllevel:
        query += ' AND Event.SkillLevel = ?'
        params.append(skilllevel)

    if cost == '0':
        query += ' AND Event.Cost = 0'
    elif cost == '1':
        query += ' AND Event.Cost != 0'

    query += '''
        ORDER BY Event.Name ASC, Event.Organization ASC
    '''

    reviews = db.execute(query, params).fetchall()

    saved = set()
    if logged_in:
        rows = db.execute("SELECT EventName, EventOrganization FROM SavedEvents WHERE UserID = ?", (session['user_id'],)).fetchall()
        saved = {(row['EventName'], row['EventOrganization']) for row in rows}

    return render_template('view/index.html', reviews=reviews, logged_in=logged_in, saved=saved)


@bp.route('/event/<organization>/<name>', methods=['GET', 'POST'])
def event_detail(name, organization):
    logged_in = 'user_id' in session

    if request.method == 'POST':
        if 'Return' in request.form:
            return redirect(url_for('view.index'))
    
    db = get_db()
    event = db.execute('SELECT * FROM Event WHERE Name = ? AND Organization = ?', (name, organization)).fetchone()
    reviews = db.execute('SELECT * FROM Review WHERE EventName = ? AND EventOrganization = ? ORDER BY PublishedAt DESC', (name, organization)).fetchall()
    return render_template('view/event_detail.html', event=event, reviews=reviews, logged_in=logged_in)

@bp.route('/reviewform', methods=['GET', 'POST'])
def reviewform():
    logged_in = 'user_id' in session
    if not logged_in:
        return redirect(url_for("auth.login"))

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
            return render_template('view/reviewform.html', events=events, logged_in=logged_in)

        name, org = full_name.split(" - ", 1)

        rating = request.form.get('rating')
        comments = request.form.get('Comments')

        error = None
        if not rating:
            error = 'Rating is required.'
        elif not comments:
            error = 'A comment is required.'

        if error:
            flash(error)
            return render_template('view/reviewform.html', events=events, logged_in=logged_in)

        rating = int(rating)
        user_id = session['user_id']

        event = db.execute(
            'SELECT 1 FROM Event WHERE Name = ? AND Organization = ?',
            (name, org)
        ).fetchone()

        if not event:
            flash("Selected event does not exist.")
            return render_template('view/reviewform.html', events=events, logged_in=logged_in)

        db.execute(
            "INSERT INTO Review (UserID, EventName, EventOrganization, Rating, Comments) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, org, rating, comments)
        )
        db.commit()
        return redirect(url_for('view.index'))

    return render_template("view/reviewform.html", events=events, logged_in=logged_in)




@bp.route('/reviewform_newevent', methods=['GET', 'POST'])
def reviewform_newevent():
    logged_in = 'user_id' in session
    if not logged_in:
        return redirect(url_for("auth.login"))

    db = get_db()

    if request.method == 'POST':
        if 'Cancel' in request.form:
            return redirect(url_for('view.index'))

        event = request.form.get('EventName')
        org = request.form.get('Organization')
        rating = request.form.get('rating')
        level = request.form.get('SkillLevel')
        cost = request.form.get('Cost')
        duration = request.form.get('Duration')
        medium = request.form.get('Medium')
        info =request.form.get('Info')
        comments = request.form.get('Comments')
        tags = request.form.get('Tags')

        error = None
        if not event:
            error = 'Event name is required.'
        elif not org:
            error = 'Organization is required.'
        elif not rating:
            error = 'Rating is required.'
        elif not level:
            error = 'Skill Level is required.'
        elif not cost:
            error = 'Cost is required.'
        elif not duration:
            error = 'Duration is required.'
        elif not medium:
            error = 'Medium is required.'
        elif not info:
            info = 'A description of the event is required.'
        elif not comments:
            error = 'A comment is required.'
        elif not tags:
            error = 'Tags are required.'

        if error:
            flash(error)
            return render_template('view/reviewform_newevent.html', logged_in=logged_in)

        rating = int(rating)
        user_id = session['user_id']

        db.execute(
            "INSERT INTO Event (Name, Organization, Medium, Duration, SkillLevel, Info, Tags, Cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (event, org, medium, duration, level, info, tags, cost)
        )
        db.execute(
            "INSERT INTO Review (UserID, EventName, EventOrganization, Rating, Comments) VALUES (?, ?, ?, ?, ?)",
            (user_id, event, org, rating, comments)
        )
        db.commit()
        return redirect(url_for('view.index'))

    return render_template("view/reviewform_newevent.html", logged_in=logged_in)

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    logged_in = 'user_id' in session
    if not logged_in:
        return redirect(url_for("auth.login"))
    
    db = get_db()

    if request.method == 'POST':
        if 'remove' in request.form:
            event_name = request.form['EventName']
            event_org = request.form['EventOrganization']

            existing = db.execute(
                "SELECT 1 FROM SavedEvents WHERE UserID = ? AND EventName = ? AND EventOrganization = ?",
                (session['user_id'], event_name, event_org)
            ).fetchone()

            if existing:
                db.execute(
                    "DELETE FROM SavedEvents WHERE UserID = ? AND EventName = ? AND EventOrganization = ?",
                    (session['user_id'], event_name, event_org)
                )
                db.commit()
                flash(f"Removed saved event: {event_name} - {event_org}")

    saved_events = db.execute(
        """
        SELECT SavedEvents.UserID, SavedEvents.EventName, SavedEvents.EventOrganization, Event.Info
        FROM SavedEvents
        JOIN Event ON SavedEvents.EventName = Event.Name AND SavedEvents.EventOrganization = Event.Organization
        WHERE SavedEvents.UserID = ?
        ORDER BY SavedEvents.EventName ASC
        """,
        (session['user_id'],)
    ).fetchall()
    user_reviews = db.execute("SELECT * FROM Review WHERE UserID = ? ORDER BY PublishedAt DESC",
                              (session['user_id'],)
                              ).fetchall()

    return render_template("view/profile.html", saved_events=saved_events, user_reviews=user_reviews, logged_in=logged_in)
