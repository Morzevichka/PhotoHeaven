from app import app, db
from app.forms import LoginForm, RegisterForm
from flask import flash, redirect, request, url_for, render_template, send_from_directory, abort
from flask_login import current_user, login_user, logout_user
from config import uploadsdir, ALLOWED_EXTENSIONS
import os
from app.models import User
import shutil
from werkzeug.utils import secure_filename


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
        # for table_name in db.metadata.tables:
        #     db.session.execute(db.table(table_name).delete())
        # db.session.commit()
        # return redirect(url_for("index"))
    return render_template("root.html", route=action, users=users, title="Admin Panel")

@app.route("/account", methods=["POST", "GET"])
def account():
    list_of_files = [str(file) for file in os.listdir(os.path.join(uploadsdir, str(current_user.id)))]
    name_photo_delete = request.args.get("delete")
    if name_photo_delete is not None:
        os.remove(os.path.join(uploadsdir, str(current_user.id), str(name_photo_delete)))
        return redirect(url_for("account"))
    return render_template("account.html", title=current_user.username, photos=list_of_files)

@app.route("/post")
def makepost():
    return render_template("base.html", title="Make Post")

@app.route("/upload", methods=["POST"])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'warning')
            return redirect(url_for("account"))
        file = request.files['file']
        if file.name == '':
            flash('No selected file', 'warning')
            return redirect(url_for("account"))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(uploadsdir, str(current_user.id), filename))
            return redirect(url_for("account"))
    return redirect(url_for("account"))

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS