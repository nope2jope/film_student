from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired
from typing import Callable
from tmdb_search import SearchBot
import os

TMDB_API_KEY = os.environ['ENV_API']

# prevents highlighting in yet-to-be-called Movie class while working on app — just a visual thing
class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    Float: Callable
    String: Callable
    Integer: Callable


app = Flask(__name__)

# bootstraps application
Bootstrap(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# creates database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-collection.db'

# spares meddlesome depreciation/overhead warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# adds custom class above to database
db = MySQLAlchemy(app)

# that this class-model is created (i.e. create_all) is what determines the nullable status
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(80), unique=True, nullable=False)
    rating = db.Column(db.String, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(80), nullable=True)
    img_url = db.Column(db.String(80), nullable=False)

# TODO make these fields optional / autofill with present info
class EditForm(FlaskForm):
    rating = FloatField('Updated Rating', validators=[DataRequired()])
    review = StringField('Updated Review', validators=[DataRequired()])
    ranking = StringField('Updated Ranking', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


# creates database if doesn't already exist
if not os.path.exists('film_faker/movie-collection.db'):
    db.create_all()


@app.route('/')
def home():
    all_movies = db.session.query(Movie).order_by(desc(Movie.ranking)).all()
    # all_movies = db.session.query(Movie)
    return render_template('index.html', movies=all_movies)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def edit(id):
    target_movie = Movie.query.get(id)
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        target_movie.rating = edit_form.rating.data
        target_movie.review = edit_form.review.data
        target_movie.ranking = edit_form.ranking.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('edit.html', movie=target_movie, form=edit_form)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    target_movie = Movie.query.get(id)
    db.session.delete(target_movie)
    db.session.commit()

    return redirect(url_for('home'))

## rework add() to incorportate API — cut down on typing

@app.route('/add', methods=['GET', 'POST'])
def add():
    add_form = AddForm()
    results = []
    x = len(results)

    if add_form.validate_on_submit():

        search_title = add_form.title.data
        detective = SearchBot(api_key=TMDB_API_KEY)
        results = detective.scour(search_title)
        x = len(results)

        return render_template('select.html', results=results, x=x)

    return render_template('add.html', form=add_form, results=results, x=x)

@app.route('/select/<string:id>', methods=['GET', 'POST'])
def select(id):
    search_id = id

    detective = SearchBot(api_key=TMDB_API_KEY)
    result = detective.pinpoint(search_id)
    new_movie = Movie(title=result['title'], year=result['year'], description=result['description'], img_url=result['poster'])

    db.session.add(new_movie)
    db.session.commit()


    return redirect(url_for('edit', id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
