from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import Column, Integer, String, Text
from flask_ckeditor import CKEditor
from forms import CreatePostForm
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


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=False, nullable=False)
    subtitle = Column(String(250), nullable=False)
    date = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    img_url = Column(String(250), nullable=False)

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


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    ckeditor.init_app(app, CKEDITOR_SERVE_LOCAL=True)