# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from data import db, Movie, Review

app = Flask(__name__)
app.secret_key = "super-secret-key"

@app.route("/")
def index():
    query = request.args.get("q", "")
    genre =185 = request.args.get("genre", "")
    movies = db.search(query) if query else db.movies
    if genre:
        movies = [m for m in movies if m.genre.lower() == genre.lower()]
    genres = sorted({m.genre for m in db.movies})
    return render_template("index.html", movies=movies, genres=genres, query=query, selected_genre=genre)

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        flash("Movie not found!")
        return redirect("/")
    return render_template("movie.html", movie=movie)

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        movie = Movie(
            title=request.form["title"],
            year=int(request.form["year"]),
            genre=request.form["genre"],
            director=request.form["director"],
            description=request.form.get("description", ""),
            poster_url=request.form.get("poster_url", "")
        )
        db.movies.append(movie)
        flash("Movie added successfully!")
        return redirect(url_for("movie_detail", movie_id=movie.id))
    return render_template("add_movie.html")

@app.route("/movie/<int:movie_id>/review", methods=["POST"])
def add_review(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if movie:
        review = Review(
            author=request.form["author"],
            text=request.form["text"],
            rating=int(request.form["rating"])
        )
        movie.reviews.append(review)
        flash("Review added!")
    return redirect(url_for("movie_detail", movie_id=movie_id))

if __name__ == "__main__":
    app.run(debug=True)