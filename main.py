from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, IntegerField
from wtforms.validators import DataRequired, URL
from typing import Callable
import os


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


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(80), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(80), nullable=False)
    img_url = db.Column(db.String(80), nullable=False)


class EditForm(FlaskForm):
    rating = FloatField('Updated Rating', validators=[DataRequired()])
    review = StringField('Updated Review', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    year = IntegerField('Release Year', validators=[DataRequired()])
    description = StringField('Movie Description', validators=[DataRequired()])
    rating = FloatField('Movie Rating', validators=[DataRequired()])
    ranking = IntegerField('Movie Ranking, 1-10', validators=[DataRequired()])
    review = StringField('Movie Review', validators=[DataRequired()])
    img_url = StringField('Movie Image', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')


# creates database if doesn't already exist
if not os.path.exists('film_faker/movie-collection.db'):
    db.create_all()

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)

db.session.add(new_movie)
db.session.commit()


@app.route('/')
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def edit(id):
    target_movie = Movie.query.get(id)
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        target_movie.rating = edit_form.rating.data
        target_movie.review = edit_form.review.data
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

    if add_form.validate_on_submit():
        new_movie = Movie(
            title=add_form.title.data,
            year=add_form.year.data,
            description=add_form.description.data,
            rating=add_form.rating.data,
            ranking=add_form.ranking.data,
            review=add_form.review.data,
            img_url=add_form.img_url.data
        )

        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for('home'))


    return render_template('add.html', form=add_form)


if __name__ == '__main__':
    app.run(debug=True)
