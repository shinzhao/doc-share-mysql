# Python libraries
from flask import Flask, render_template, redirect, request, flash, url_for, session
from functools import wraps
import mysql.connector

# Local files
from DatabaseController import DatabaseController
from forms import *

# Set up flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

# Configuration to database
config = {
    'user': "root",
    'password': "root",
    'host': "127.0.0.1",
    'port': "3306",
    'database': "docshare"
}
dbcontroller = DatabaseController(config)

# Check if a user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if session['logged_in']:
                return f(*args, **kwargs)
        except:
            pass

        flash('Please log in!', 'danger')
        return redirect(url_for('home'))
    return wrap

# Check if a user is admin
def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if session['user_type'] == 'admin':
                return f(*args, **kwargs)
        except:
            pass

        flash("You don't! have access to this page!", 'danger')
        return redirect(url_for('home'))
    return wrap

# Log out
@app.route('/log_out')
@is_logged_in
def log_out():
    session.clear()
    flash('You are logged out.', 'success')
    return redirect(url_for('home'))

######################
#    Public Pages
######################

# Home page and login
@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if session['logged_in'] == True:
            return redirect(url_for('user_page'))
    except:
        pass

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        log_in_status = dbcontroller.log_in(username, password)
        if log_in_status == 1:
            session['logged_in'] = True
            session['username'] = username
            session['user_type'] = dbcontroller.get_user_type(username)
            flash(f'Hello, {username}!', 'success')
            return redirect(url_for('user_page'))
        elif log_in_status == 0:
            flash('Login failed, please try again!', 'danger')
        elif log_in_status == -1:
            flash('Your account has been banned!', 'danger')

    return render_template('home.html')


# Sign up
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = RegForm(request.form)

    if request.method == 'POST' and form.validate():
        if dbcontroller.sign_up(form.username.data, form.password.data, form.email.data, form.firstName.data, form.lastName.data):
            flash('You successfully signed up!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Username is taken!', 'danger')
            return render_template('sign_up.html', form=form)

    return render_template('sign_up.html', form=form)


# Public document list
@app.route('/docs', methods=['GET'])
def docs():
    docs = dbcontroller.get_docs_public()
    # If docs not empty
    if docs:
        return render_template('docs.html', docs=docs)
    else:
        return render_template('docs.html', msg='No Document Found')


# Public document content
@app.route('/doc/<string:id>', methods=['GET'])
def doc(id):
    # User logged in
    try:
        if session['logged_in'] == True:
            doc = dbcontroller.get_doc_by_id(id, session['username'])
            # Have access to doc
            if doc:
                return render_template('doc.html', doc=doc)
            # No access to doc
            else:
                flash("You don't have access to this document!", 'danger')
                return redirect(url_for('docs'))
    # User not logged in
    except:
        doc = dbcontroller.get_doc_by_id(id)
        # Have access to doc
        if doc:
            return render_template('doc.html', doc=doc)
        # No access to doc
        else:
            flash("You don't have access to this document!", 'danger')
            return redirect(url_for('docs'))


# About
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


##########################
#     Main User Page
##########################

# Dashboard
@app.route('/user_page')
@is_logged_in
def user_page():
    if session['user_type'] == 'admin':
        docs = dbcontroller.get_docs_admin()
    else:
        docs = dbcontroller.get_docs_user(session['username'])
    # If docs not empty
    if docs:
        return render_template('user_page.html', docs=docs)
    else:
        return render_template('user_page.html', msg='No Document Found')


################################
#  Document Manipulation Pages
################################

# Create document
@app.route('/create_doc', methods=['GET', 'POST'])
@is_logged_in
def create_doc():
    form = DocForm(request.form)
    if request.method == 'POST' and form.validate():
        if dbcontroller.create_doc(form.title.data, session['username'], form.content.data, form.is_private.data):
            flash('Document created!', 'success')
            return redirect('/')

    return render_template('create_doc.html', form=form)


# Edit document
@app.route('/edit_doc/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_doc(id):
    doc = dbcontroller.get_doc_by_id(id, session['username'])

    form = DocForm(request.form)
    form.title.data = doc['title']
    form.content.data = doc['content']
    form.is_private.data = True if doc['status'] == 'private' else False

    if request.method == 'POST' and form.validate():
        form = DocForm(request.form)
        if dbcontroller.edit_doc(id, form.title.data, form.content.data, form.is_private.data):
            dbcontroller.edit_hist(
                id, doc['title'], session['username'], doc['content'], doc['modify_date'])
            flash('Document updated!', 'success')
            return redirect('/user_page')

    return render_template('edit_doc.html', form=form, owner=doc['owner'])


# Delete document
@app.route('/delete_doc/<string:id>', methods=['POST'])
@is_logged_in
def delete_doc(id):
    dbcontroller.delete_doc(id)
    flash('Document deleted!', 'success')
    return redirect('/user_page')


# Document history list
@app.route('/doc_hist_list/<string:id>', methods=['GET'])
@is_logged_in
def doc_hist_list(id):
    hist_list, empty = dbcontroller.get_hist_list(id, session['username'])

    if hist_list or empty:
        if hist_list:
            return render_template('doc_hist_list.html', docs=hist_list)
        else:
            flash("This document has no history.", 'warning')
            return redirect(url_for('home'))
    else:
        flash("You don't have access to this document!", 'danger')
        return redirect(url_for('home'))


# History version document
@app.route('/doc_hist/<string:id>', methods=['GET'])
@is_logged_in
def doc_hist(id):
    # User logged in
    try:
        if session['logged_in'] == True:
            doc = dbcontroller.get_doc_hist_by_id(id, session['username'])
            # Have access to doc
            if doc:
                return render_template('doc_hist.html', doc=doc)
            # No access to doc
            else:
                flash("You don't have access to this document!", 'danger')
                return redirect(url_for('home'))
    # User not logged in
    except:
        flash("You don't have access to this page!", 'danger')
        return redirect(url_for('home'))


#####################
#  Management Page
#####################

# Manage users
@app.route('/manage_users')
@is_admin
def manage_users():
    users = dbcontroller.get_all_users()
    return render_template('manage_users.html', users=users, username=session['username'])

# Make user
@app.route('/make_user/<string:id>')
@is_admin
def make_user(id):
    dbcontroller.make_user(id)
    return redirect(url_for('manage_users'))

# Make admin
@app.route('/make_admin/<string:id>')
@is_admin
def make_admin(id):
    dbcontroller.make_admin(id)
    return redirect(url_for('manage_users'))

# Ban user
@app.route('/ban_user/<string:id>')
@is_admin
def ban_user(id):
    dbcontroller.ban_user(id)
    return redirect(url_for('manage_users'))

# Unban user
@app.route('/unban_user/<string:id>')
@is_admin
def unban_user(id):
    dbcontroller.unban_user(id)
    return redirect(url_for('manage_users'))

#####################
#   Run app server
#####################
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
