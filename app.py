# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from data import db, Movie, Review
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key-change-in-production")

# ────────────────────────── ADMIN AUTH ──────────────────────────
# Change this password to anything you want (keep the quotes)
ADMIN_PASSWORD = "MySuperSecretPassword2025!"

def check_auth():
    auth = request.authorization
    return auth and auth.username == "admin" and auth.password == ADMIN_PASSWORD

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth():
            return Response(
                'Login required to access this page.',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            )
        return f(*args, **kwargs)
    return decorated
# ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()

    movies = db.movies

    if query:
        query_lower = query.lower()
        movies = [m for m in movies if query_lower in m.title.lower() or query_lower in m.director.lower() or query_lower in m.genre.lower()]

    if genre:
        movies = [m for m in movies if m.genre.lower() == genre.lower()]

    genres = sorted({m.genre for m in db.movies})

    return render_template(
        "index.html",
        movies=movies,
        genres=genres,
        query=query,
        selected_genre=genre
    )

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        flash("Movie not found!", "error")
        return redirect("/")
    return render_template("movie.html", movie=movie)

@app.route("/add", methods=["GET", "POST"])
@requires_auth          # ← PROTECTED
def add_movie():
    if request.method == "POST":
        try:
            new_movie = Movie(
                title=request.form["title"].strip(),
                year=int(request.form["year"]),
                genre=request.form["genre"].strip(),
                director=request.form["director"].strip(),
                description=request.form.get("description", "").strip(),
                poster_url=request.form.get("poster_url", "").strip()
@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        flash("Movie not found!", "error")
        return redirect("/")
    return render_template("movie.html", movie=movie)


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        try:
            new_movie = Movie(
                title=request.form["title"].strip(),
                year=int(request.form["year"]),
                genre=request.form["genre"].strip(),
                director=request.form["director"].strip(),
                description=request.form.get("description", "").strip(),
                poster_url=request.form.get("poster_url", "").strip() or ""
            )
            db.movies.append(new_movie)
            flash("Movie added successfully!", "success")
            return redirect(url_for("movie_detail", movie_id=new_movie.id))
        except Exception as e:
            flash("Error adding movie. Please check your input.", "error")

    return render_template("add_movie.html")


@app.route("/movie/<int:movie_id>/review", methods=["POST"])
def add_review(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        flash("Movie not found!", "error")
        return redirect("/")

    author = request.form["author"].strip() or "Anonymous"
    text = request.form["text"].strip()
    rating = int(request.form["rating"])

    if not text:
        flash("Review text is required.", "error")
    elif rating < 1 or rating > 5:
        flash("Rating must be 1–5.", "error")
    else:
        movie.reviews.append(Review(author, text, rating))
        flash("Thank you! Your review was added.", "success")

    return redirect(url_for("movie_detail", movie_id=movie_id))


# ------------------------------------------------------------------
# Run server (local + production)
# ------------------------------------------------------------------

if __name__ == "__main__":
    # Local development
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    # Production platforms (Render, Railway, Fly.io, etc.)
    # Waitress is lightweight, production-ready, and works great on free tiers
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Waitress server on port {port}...")
    serve(app, host="0.0.0.0", port=port)
