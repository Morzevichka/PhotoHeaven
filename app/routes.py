from app import app
import os
from flask import render_template, send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 
                               'favicon.ico')


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/seach")
def search_page():
    return render_template("base.html")

@app.route("/lk")
def accout():
    return render_template("base.html") 

@app.route("/login")
def login():
    return render_template("base.html")

@app.route("/register")
def register():
    return render_template("base.html")