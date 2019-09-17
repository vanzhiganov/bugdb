"""BugDB 2019"""
import validators
from flask import Flask, request, session, g, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import alias
from flask_migrate import Migrate

from BugDB import db, emails

# from app.bugdb import models

app = Flask(__name__)
app.config.from_pyfile('config.py')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/vanzhiganov/Develop/bugdb/app.db'

# database = SQLAlchemy(app)
db.database.init_app(app)
migrate = Migrate(app, db.database)

from BugDB.Models import UsersModel, BugHeaderModel, BugBodyModel, StatusesModel


@app.before_request
def before_request():
    # g.db = db.connect_db()
    pass


@app.after_request
def after_request(response):
    # g.db.commit()
    # g.db.close()
    return response


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('queue'))
    return render_template('pages/index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not validators.email(email):
            flash('Invalid email', 'danger')
            return render_template('pages/login.html')

        debug('Before trying to login with email_id %s' % email)

        user = UsersModel.login(email, password)

        if not user:
            flash('Login failed. Try again', 'warning')
            return render_template('pages/login.html')

        debug('Login successful for email_id : ' + email)

        # user = db.getUser(g.db, username)

        session['id'] = user.id
        session['username'] = str(user.username)
        session['email'] = user.email
        debug('user found and session populated with : ' + user.email)

        return redirect(url_for('queue'))
    return render_template('pages/login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if its there
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    debug('logged out successfully')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # TODO: validate email
        email = request.form.get('email')
        password = request.form.get('password')

        if not validators.email(email):
            flash('Invalid email', 'danger')
            return render_template('pages/register.html')

        debug('Registering new User: %s' % email)

        if not UsersModel.is_exists_email(email):
            u = UsersModel(email, UsersModel.get_hash(password), username=email)
            db.database.session.add(u)
            db.database.session.commit()
            db.database.session.flush()

        return redirect(url_for('login'))
    return render_template('pages/register.html')


@app.route('/queue', methods=['GET', 'POST'])
def queue():
    if 'username' not in session:
        return render_template('login.html', error='Login first')

    users = db.database.session.query(UsersModel.id, UsersModel.email, UsersModel.username).all()

    if request.method != 'POST':
        debug('Getting bugList for user : ' + session['username'])

        bug_list = db.database.session.query(
            BugHeaderModel.id,
            BugHeaderModel.title,
            BugHeaderModel.priority,
            BugHeaderModel.customer,
            BugHeaderModel.status,
            UsersModel.id.label('user_id'),
            UsersModel.email,
            UsersModel.username,
        ).filter(
            BugHeaderModel.assigned_to_user_id == UsersModel.id
        ).filter(
            UsersModel.id == session['id']
        ).all()

        for o in bug_list:
            print(dir(o))

        return render_template(
            'pages/queue.html',
            bugs=bug_list,
            other_username=session['username'],
            users=users,
            queue_user=session['username'])
    else:

        if request.form['other_user_id'] != 'all':
            # debug('Getting bugList for user : ' + request.form['other_user_id'])
            # bugList = db.getBugList(g.db, request.form['other_username'])

            bug_list = db.database.session.query(
                BugHeaderModel.id,
                BugHeaderModel.title,
                BugHeaderModel.priority,
                BugHeaderModel.customer,
                BugHeaderModel.status,
                UsersModel.id,
                UsersModel.email,
                UsersModel.username,
            ).filter(
                BugHeaderModel.assigned_to_user_id == UsersModel.id
            ).filter(
                UsersModel.id == int(request.form['other_user_id'])
            ).all()

            return render_template(
                'pages/queue.html',
                bugs=bug_list,
                other_user_id=request.form['other_user_id'],
                users=users,
                queue_user=request.form['other_user_id'])
        else:
            debug('Getting all queues')
            # get a visible drop down of all users.
            # avallark working from here...
            # create an list of list of users
            all_queues = db.getAllQueues(g.db)
            return render_template(
                'pages/all_queues.html',
                all_queues=all_queues,
                users=users,
                other_username="All")


@app.route('/addBug', methods=['GET', 'POST'])
def addBug():
    if 'username' not in session:
        return render_template('pages/login.html', error='Login first')

    if request.method == 'POST':
        debug('Creating the bug dictionary for the username : ' + session['username'])

        # user = db.getUser(g.db, session['username'])

        user = db.database.session.query(
            UsersModel.id, UsersModel.email, UsersModel.username
        ).filter_by(id=session['id']).first()

        print(user)

        if user:

            user_id = user.id

            debug('Building dictionary before creating bug for user_id : ' + str(user_id))

            debug('Calling db.createBug2 for bug ' + request.form['title'])

            bug = BugHeaderModel()
            bug.title = request.form['title']
            bug.customer = request.form['customer']
            bug.assigned_to_user_id = user.id
            bug.description = request.form['description']
            bug.priority = request.form['priority']
            bug.status = "OPEN"

            db.database.session.add(bug)
            db.database.session.commit()
            db.database.session.flush()

            debug('Created the above bug')
            return redirect(url_for('queue'))
        else:
            return redirect(url_for('queue'))
    return render_template('pages/createbug.html')


@app.route('/bug', methods=['GET', 'POST'])
def bug():
    bug_id = request.args.get('bug_id', '')
    if request.method != 'POST':
        debug('Calling getBugHeader')

        bugh = db.database.session.query(BugHeaderModel).filter_by(id=bug_id).first()
        print(bugh)

        debug('Calling getBugBody')

        # bugb = db.getBugBody(g.db, bug_id)
        bugb = db.database.session.query(
            BugBodyModel.bug_update,
            BugBodyModel.updated_at,
            BugBodyModel.updated_by,
            UsersModel.id.label("user_id"),
            UsersModel.username,
            UsersModel.email,
        ).filter(
            BugBodyModel.bug_id == bug_id
        ).filter(
            UsersModel.id == BugBodyModel.updated_by
        ).all()

        all_status = db.database.session.query(StatusesModel).all()
        all_users = db.database.session.query(UsersModel.id, UsersModel.email, UsersModel.username).all()

        return render_template(
            'pages/bug.html', bugh=bugh, bugb=bugb, all_status=all_status, all_users=all_users)

    else:
        print(request.form)
        debug('Creating dictionary of bug to update the header for ' + str(bug_id))

        updated_by_user_id = request.form['updated_by_user_id']
        assigned_to_user_id = db.database.session.query(UsersModel.id).filter_by(id=updated_by_user_id).scalar()
        updating_user_id = db.database.session.query(UsersModel.id).filter_by(id=session['id']).scalar()

        bug = dict(
            title=request.form['title'],
            customer=request.form['customer'],
            updated_by_username=session['username'],
            assigned_to_user_id=assigned_to_user_id,
            assigned_to_username=request.form['assigned_to_user'],
            description=request.form['description'],
            priority=request.form['priority'],
            status=request.form.get('status', 'OPEN'),
            updating_user_id=updating_user_id,
            bug_id=bug_id
        )

        # creating list of header updates onto the body
        debug(str(bug_id))

        bugh = db.database.session.query(BugHeaderModel).filter_by(id=bug_id).first()

        changedString = ""

        if bugh.title != bug['title']:
            changedString += "** Changed Title from " + bugh.title + " to " + bug['title'] + "\n"

            bugh.title = bug['title']

        # if bugh['description'] <> bug['description']:
        #    changedString += "** Changed Description from "+bugh['description']+" to "+ bug['description'] + "\n"

        if bugh.assigned_to_user_id != int(bug['assigned_to_user_id']):
            to = UsersModel.get_email_by_id(bug['assigned_to_user_id'])
            debug('Sending email to notify assignation to : ' + to)
            changedString += "** Changed Assigned from " + bugh.assigned_to_user_id + " to " + request.form[
                'assigned_to_username'] + "\n"
            debug(changedString)
            emails.bugAssignNotify(bug, to)

            bugh.assigned_to_user_id = bug['assigned_to_user_id']

        if bugh.description != bug['description']:
            changedString += "** Changed Bug Description from " + "\n" + bugh.description + " to " + bug['description'] + "\n"
            bugh.description = bug['description']

        if bugh.customer != bug['customer']:
            changedString += "** Changed Customer from " + bugh.customer + " to " + bug['customer'] + "\n"
            bugh.customer = bug['customer']

        if bugh.status != bug['status']:
            changedString += "** Changed Status from " + bugh.status + " to " + bug['status'] + "\n"

        if str(bugh.priority) != str(bug['priority']):
            changedString += "** Changed Priority from " + str(bugh.priority) + " to " + str(bug['priority']) + "\n"
            bugh.priority = int(bug['priority'])

        debug(changedString)
        # Now updating the header with changes
        # db.updateBugHeader(g.db, bug)

        bb = BugBodyModel()
        bb.bug_update = changedString + "\n" + request.form['newupdate']
        bb.updated_by = updating_user_id
        bb.bug_id = bug_id

        db.database.session.add(bb)
        db.database.session.commit()
        db.database.session.flush()

        return redirect(url_for('queue'))


# setup urls

@app.route('/options')
def options():
    return render_template('pages/options.html')


@app.route('/categories')
def categories():
    return render_template('pages/categories.html')


@app.route('/status', methods=['GET', 'POST'])
def status():
    if request.method == 'POST':
        debug('Adding the status : ' + request.form['status'])
        s = StatusesModel()
        s.status = request.form['status']
        s.description = request.form['description']

        db.database.session.add(s)
        db.database.session.commit()
        db.database.session.flush()

    status = db.database.session.query(StatusesModel).all()
    return render_template('pages/status.html', status=status)


@app.route('/deleteStatus')
def deleteStatus():
    status = request.args.get('status', '')
    StatusesModel.query.filter_by(status=status).delete()
    return redirect(url_for('status'))


# Usual debug procedures

def debug(t):
    """
    The procedure logs all comments if the DEBUG configuration variable is set to True
    """
    # if app.config['DEBUG']:
    #     db.m_debug(g.db, t)
    pass


@app.route('/add')
def add():
    debug(session['username'])
    return redirect(url_for('debugs'))


@app.route('/debugs')
def debugs():
    debug_log = db.getDebug(g.db)
    return render_template('pages/debug.html', debug=debug_log)


@app.route('/flushDebug')
def flushDebug():
    debug('Entering Flush Debug')
    db.flushDebug(g.db)
    return redirect(url_for('debugs'))


# and finally lets start the program.
if __name__ == '__main__':
    #    if app.config.ENVIR != app.config.DEV:
    #        app.run(host='0.0.0.0', port=4000)
    #    else:
    # DEBUG = False
    app.run(port=4000)
