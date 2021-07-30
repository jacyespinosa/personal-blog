from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import Column, Integer, ForeignKey, String, Text


app = Flask(__name__)
app.config['SECRET_KEY'] = "ENTER SECRET KEY"
Bootstrap(app)


#CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)