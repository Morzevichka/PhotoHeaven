from app import app
from app import db
from app.forms import RegisterForm, LoginForm
from app.entity import User
import os
from flask import render_template, send_from_directory, flash, request, redirect, url_for
from flask_login import current_user, login_user, logout_user

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 
                               'favicon.ico')

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/singup", methods=["POST", "GET"])
def register(): 
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Login is taken', 'warning') #fix this flash
            return redirect(url_for("index"))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Successful Sign up! Your Id is {user.id}', 'success')
        login_user(user)
        return redirect(url_for("index"))
    return render_template("register.html", title='Sing up', form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
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
    return render_template('login.html', title="Sign in", form=form)

@app.route("/lk")
def account():
    return render_template("base.html", title="Account") 

@app.route("/admin", methods=["POST", "GET"])
def admin():
    action = request.args.get("action", "")
    username = request.args.get("username")
    status = request.args.get("status")
    users = User.query.all()
    if action == "delete":
        user_to_delete = User.query.filter_by(username=username).first()
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
                db.session.delete(user)
                db.session.commit()
        # for table_name in db.metadata.tables:
        #     db.session.execute(db.table(table_name).delete())
        # db.session.commit()
        # return redirect(url_for("index"))
    return render_template("root.html", route=action, users=users)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have logged out', 'warning')
    return redirect(url_for('index'))