from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail, Message

with open('config.json', 'r') as c:
    prams = json.load(c)['prams']
app = Flask(__name__)
app.secret_key = 'the random string'
local_server = True

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = prams['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = prams['prod_uri']
app.config.update(dict(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USERNAME=prams['gmail-user'],
    MAIL_PASSWORD=prams['gmail-password'],
    MAIL_SSL=True
))
db = SQLAlchemy(app)
mail = Mail(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(20), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=False, nullable=False)
    mes = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(120), unique=False, nullable=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=False, nullable=False)
    content = db.Column(db.String(300), unique=False, nullable=False)
    tagline = db.Column(db.String(30), unique=False, nullable=False)
    slug = db.Column(db.String(25), unique=False, nullable=False)
    img_path = db.Column(db.String(25), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:prams['number_posts']]
    return render_template('index.html', prams=prams, posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', prams=prams)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        date1 = datetime.now()
        entry = Contact(name=name, email=email, phone_num=phone, mes=message, date=date1)
        db.session.add(entry)
        db.session.commit()
        msg = Message(message, sender=(prams['gmail-user']), recipients=[email])
        mail.send(msg)
    return render_template('contact.html', prams=prams)


@app.route("/post/<string:pslug>", methods=['GET'])
def post_route(pslug):
    post = Posts.query.filter_by(slug=pslug).first()
    return render_template('post.html', prams=prams, post=post)


@app.route("/login", methods=['GET', 'POST'])
def login():
    post = Posts.query.filter_by().all()
    if 'uname' in session and session['uname'] == prams['usernme']:
        return render_template('dashboard.html', prams=prams, post=post)
    if request.method == 'POST':
        user = request.form.get('username')
        passw = request.form.get('password')
        if user == prams['usernme'] and passw == prams['password']:
            session['uname'] = user
            return render_template('dashboard.html', prams=prams, post=post)
    return render_template('login.html')


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    post = Posts.query.filter_by().all()
    if 'uname' in session and session['uname'] == prams['usernme']:
        render_template('edit.html', prams=prams, post=post)
        if request.method == 'POST':
            render_template('edit.html', prams=prams, post=post)
            ptitle = request.form.get('title')
            tline = request.form.get('tline')
            content = request.form.get('content')
            imgp = request.form.get('imgp')
            slug = request.form.get('slug')
            if sno == '0':
                date1 = datetime.now()
                entry = Posts(title=ptitle, tagline=tline, img_path=imgp, content=content, date=date1, slug=slug)
                db.session.add(entry)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = ptitle
                post.tagline = tline
                post.content = content
                post.img_path = imgp
                post.slug = slug
                db.session.commit()
                return redirect("/edit/" + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', prams=prams, post=post, sno=sno)

@app.route("/logout")
def logout():
    session.pop('uname')
    return redirect("/login")




app.run(debug=True)
