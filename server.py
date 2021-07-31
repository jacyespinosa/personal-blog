from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import Column, Integer, String, Text
from flask_ckeditor import CKEditor
from forms import CreatePostForm, RegisterForm, LogInForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = "ENTER SECRET KEY"
Bootstrap(app)


#CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#CKEDITOR USED TO ADD BLOG POST OR TO POST COMMENTS
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'full'


#FLASK-LOGIN
login_manager = LoginManager()
login_manager.init_app(app)


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=False, nullable=False)
    subtitle = Column(String(250), nullable=False)
    date = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    img_url = Column(String(250), nullable=False)

    def to_dict(self):
        dictionary = {}

        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


#CREATE USER TABLE IN THE posts.db DATABASE
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    name = Column(String(1000))



#Line below only required once, when creating DB.
db.create_all()


@app.route('/')
def get_all_posts():
    all_posts = BlogPost.query.all()
    return render_template("index.html", all_posts=all_posts)


@app.route("/post/<int:blog_id>", methods=["GET", "POST"])
def show_post(blog_id):
    requested_post = BlogPost.query.get(blog_id)
    return render_template("post.html", post=requested_post)


@app.route("/new_post", methods=['GET', 'POST'])
def create_post():
    form = CreatePostForm(request.form)
    now = datetime.datetime.now()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_entry = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                date=now.strftime("%B %d, %Y"),
                body=form.body.data,
                img_url=form.img_url.data
            )

            db.session.add(new_entry)
            db.session.commit()
            return redirect("/")
        else:
            flash("Please make sure the fields are filled out.")
            return render_template("make-post.html", form=form)

    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:blog_id>", methods=['GET', 'POST'])
def edit(blog_id):
    requested_post = BlogPost.query.get(blog_id)
    now = datetime.datetime.now()
    edit_form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        img_url=requested_post.img_url,
        body=requested_post.body
    )
    if edit_form.validate_on_submit():
        requested_post.title = edit_form.title.data
        requested_post.subtitle = edit_form.subtitle.data
        requested_post.date = now.strftime("%B %d, %Y")
        requested_post.body = edit_form.body.data
        requested_post.img_url = edit_form.img_url.data

        db.session.commit()
        return redirect(url_for("show_post", blog_id=requested_post.id))

    return render_template("make-post.html", form=edit_form, edit_successful=True)


@app.route("/delete/<int:blog_id>", methods=["GET", "POST", "DELETE"])
def delete(blog_id):
    post_to_delete = BlogPost.query.get(blog_id)
    if post_to_delete:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    else:
        return jsonify(error={"Not Found": "Sorry a blog post with that id was not found in the database."}), 404


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # Email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        #Email doesn't exist in the database
        else:
            # Salt/Hash the User's password
            secured_password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                password=secured_password,
            )

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))

    return render_template("register.html", form=form, user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LogInForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user_email_input = form.email.data
            user_password_input = form.password.data

            in_database = User.query.filter_by(email=user_email_input).first()
            #Check if the email exists in the database.
            if in_database:
                email_stored = in_database.email
                password_stored = in_database.password
                #Check if the entered password and email matches the ones in the database.
                if check_password_hash(password_stored, user_password_input) and (email_stored == user_email_input):
                    login_user(in_database)
                    return redirect(url_for("get_all_posts"))
                #When the user enter a password and/or email that does not exist in the database.
                else:
                    flash("Please enter the correct email/password.")
            #When the user enter a password and/or email that does not exist in the database.
            else:
                flash("Invalid credentials")

    return render_template("login.html", form=form, user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    ckeditor.init_app(app, CKEDITOR_SERVE_LOCAL=True)