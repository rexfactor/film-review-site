# app.py - Clean final version
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from data import db, Movie, Review
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key-change-in-production")

# ────────────────────────── ADMIN AUTH (for routes only) ──────────────────────────
ADMIN_PASSWORD = "MySuperSecretPassword2025!"  # Change this to your own password!

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
    show_admin = request.args.get("admin") == "true"  # URL param for admin UI

    movies = db.movies
    if query:
        q = query.lower()
        movies = [m for m in movies if q in m.title.lower() or q in m.director.lower() or q in m.genre.lower()]
    if genre:
        movies = [m for m in movies if m.genre.lower() == genre.lower()]

    genres = sorted({m.genre for m in db.movies})

    return render_template(
        "index.html",
        movies=movies,
        genres=genres,
        query=query,
        selected_genre=genre,
        show_admin=show_admin
    )

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        flash("Movie not found!", "error")
        return redirect("/")
    show_admin = request.args.get("admin") == "true"
    return render_template("movie.html", movie=movie, show_admin=show_admin)

@app.route("/add", methods=["GET", "POST"])
@requires_auth
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
        except Exception:
            flash("Error adding movie. Please check your input.", "error")
    return render_template("add_movie.html")

@app.route("/movie/<int:movie_id>/review", methods=["POST"])
@requires_auth
def add_review(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        return redirect("/")
    text = request.form["text"].strip()
    rating = int(request.form["rating"])
    if text and 1 <= rating <= 5:
        movie.reviews.append(Review("You", text, rating))
        flash("Your review was added.", "success")
    else:
        flash("Invalid review.", "error")
    redirect_url = url_for("movie_detail", movie_id=movie_id)
    if request.args.get("admin") == "true":
        redirect_url += "?admin=true"
    return redirect(redirect_url)

# ────────────────────────── SERVER START ──────────────────────────
if __name__ == "__main__":
    # Local development
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    # Production (Render, etc.)
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Waitress server on port {port}...")
    serve(app, host="0.0.0.0", port=port)
