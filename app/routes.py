from functools import wraps
from app import app, db
from app.forms import LoginForm, RegisterForm
from flask import flash, redirect, request, url_for, render_template, send_from_directory, abort
from flask_login import current_user, login_user, logout_user, login_required
from config import uploadsdir, ALLOWED_EXTENSIONS
import os
from app.models import User
import shutil
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def current_user_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            return redirect(url_for('login'))
        if current_user.username != kwargs.get('username'):
            abort(403)
        return func(*args, **kwargs)
    return decorated_function

@app.route("/singup", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        os.mkdir(os.path.join(uploadsdir, str(user.id)))
        flash(f'Successful Sign up! Your Id is {user.id}', 'success')
        login_user(user)
        return redirect(url_for("index"))
    return render_template("register.html", title='Sing up', form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect login or password', 'warning')
            return redirect(url_for("login"))
        
        if user.status != "ACTIVE":
            flash("Your account was deactivated or banned", 'danger')
            return redirect(url_for("login"))
        
        login_user(user, remember=form.remember_me.data)
        flash('Seccussful Log In', 'success')
        return redirect(url_for("index"))
    return render_template('login.html', title="Log in", form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have logged out', 'warning')
    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/admin", methods=["POST", "GET"])
def admin():
    if current_user.role != "ROOT":
        abort(403)

    action = request.args.get("action", "")
    username = request.args.get("username")
    status = request.args.get("status")
    users = User.query.all()

    if action == "delete":
        user_to_delete = User.query.filter_by(username=username).first()
        shutil.rmtree(os.path.join(uploadsdir, str(user_to_delete.id)), ignore_errors=True)
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f'User {user_to_delete.username} was successful deleted', 'success')
        return redirect("/admin?action=list_users")
    
    if status is not None:
        user = User.query.filter_by(username=username).first()
        user.status = status
        db.session.commit()
        return redirect("/admin?action=list_users")

    if action == "delete_db":
        for user in users:
            if user.role != "ROOT" or user.username != "root":
                shutil.rmtree(os.path.join(uploadsdir, str(user.id)), ignore_errors=True)
                db.session.delete(user)
                db.session.commit()
    return render_template("root.html", route=action, users=users, title="Admin Panel")

@app.route("/<username>", methods=["POST", "GET"])
def profile(username):
    user = User.query.filter_by(username=username).first()
    list_of_files = [str(file) for file in os.listdir(os.path.join(uploadsdir, str(user.id)))]
    if current_user.is_authenticated:
        if user.username == current_user.username:
            name_photo_delete = request.args.get("delete")
            if name_photo_delete is not None:
                os.remove(os.path.join(uploadsdir, str(current_user.id), str(name_photo_delete)))
                return redirect(url_for("profile", username=current_user.username))
    return render_template("profile.html", title=user.username, photos=list_of_files, user=user)

@current_user_required
@login_required
@app.route("/upload", methods=["POST"])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'warning')
            return redirect(url_for("profile", username=current_user.username))
        file = request.files['file']
        if file.name == '':
            flash('No selected file', 'warning')
            return redirect(url_for("profile", username=current_user.username))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(uploadsdir, str(current_user.id), filename))
            return redirect(url_for("profile", username=current_user.username))
    return redirect(url_for("profile", username=current_user.username))

@app.route("/search")
def search():
    username_to_find = request.args.get("username")
    list_of_users = []
    list_of_number_photo = []
    if username_to_find is not None:
        list_of_users = User.query.filter(User.username.ilike(f'%{username_to_find}%')).all()
        for user in list_of_users:
            list_of_number_photo.append(len([str(file) for file in os.listdir(os.path.join(uploadsdir, str(user.id)))]))
        print(list_of_number_photo)
        print(list_of_users)
    return render_template("search.html", list_of_users=list_of_users, list_of_number_photo=list_of_number_photo)