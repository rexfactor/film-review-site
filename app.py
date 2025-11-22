# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from data import db, Movie, Review
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key-change-in-production")

# ────────────────────────── ADMIN AUTH ──────────────────────────
ADMIN_PASSWORD = "MySuperSecretPassword2025!"   # ← change this!

def check_auth():
    auth = request.authorization
    return auth and auth.username == "admin" and auth.password == ADMIN_PASSWORD

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth():
            return Response(
                'Login required.',
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
    show_admin = request.args.get("admin") == "true"

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
            flash("Error adding movie.", "error")
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
        flash("Review added.", "success")
    else:
        flash("Invalid review.", "error")
    return redirect(url_for("movie_detail", movie_id=movie_id) + ("?admin=true" if request.args.get("admin") == "true" else ""))

# ────────────────────────── SERVER ──────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    serve(app, host="0.0.0.0", port=port)
    def _seed_data(self):
        # Starter movies with YOUR placeholder reviews (customize these!)
        inception = Movie(
            title="Inception", year=2010, genre="Sci-Fi", director="Christopher Nolan",
            description="A thief who steals corporate secrets through dream-sharing technology takes on a final job: planting an idea into the mind of a CEO.",
            poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/9gk7adHYeDkXNK0kuA7cfg5i9f8.jpg"
        )
        inception.reviews = [
            Review("You", "Nolan's layered dream worlds still haunt me — a perfect blend of heist and philosophy.", 5),
            Review("You", "The spinning top ending debate rages on, but the emotional core hits hardest.", 5)
        ]

        dune = Movie("Dune: Part Two", year=2024, genre="Sci-Fi", director="Denis Villeneuve",
                     description="Paul Atreides unites with Chani and the Fremen while seeking revenge against those who destroyed his family.",
                     poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg"
        )
        dune.reviews = [
            Review("You", "Villeneuve turns Herbert's epic into visual poetry — the sandworm rides alone are worth the ticket.", 5),
            Review("You", "Deeper themes of colonialism hit differently on rewatch; Zendaya steals every scene.", 5)
        ]

        shawshank = Movie("The Shawshank Redemption", year=1994, genre="Drama", director="Frank Darabont",
                          description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                          poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
        )
        shawshank.reviews = [
            Review("You", "Timeless tale of hope — 'Get busy living or get busy dying' is etched in my brain forever.", 5),
            Review("You", "Freeman and Robbins' chemistry carries the quiet moments; underrated score too.", 5)
        ]

        oppenheimer = Movie("Oppenheimer", year=2023, genre="Biography", director="Christopher Nolan",
                            description="The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
                            poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg"
        )
        oppenheimer.reviews = [
            Review("You", "A ticking-clock biopic that explodes into moral horror — Murphy's intensity is unmatched.", 5),
            Review("You", "The black-and-white interludes add genius layers; left me rethinking history.", 5)
        ]

        self.movies.extend([inception, dune, shawshank, oppenheimer])

    def search(self, query: str) -> List[Movie]:
        query = query.lower()
        return [m for m in self.movies if query in m.title.lower() or query in m.director.lower() or query in m.genre.lower()]

db = Database()  # Singleton instance    movies = db.movies

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
        selected_genre=genre,
        show_admin=show_admin  # ← PASS URL PARAM TO TEMPLATE
    )

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        flash("Movie not found!", "error")
        return redirect("/")
    
    show_admin = request.args.get("admin") == "true"  # ← NEW: URL toggle here too
    
    return render_template("movie.html", movie=movie, show_admin=show_admin)

@app.route("/add", methods=["GET", "POST"])
@requires_auth          # ← STILL PROTECTED
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
            flash("Error adding movie.", "error")

    return render_template("add_movie.html")

@app.route("/movie/<int:movie_id>/review", methods=["POST"])
@requires_auth          # ← STILL PROTECTED
def add_review(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        return redirect("/")

    author = request.form.get("author", "You").strip() or "You"
    text = request.form["text"].strip()
    rating = int(request.form["rating"])

    if text and 1 <= rating <= 5:
        movie.reviews.append(Review(author, text, rating))
        flash("Your review was added.", "success")
    else:
        flash("Invalid review.", "error")

    return redirect(url_for("movie_detail", movie_id=movie_id))

# ───── Server start (local + production) ─────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Waitress on port {port}...")
    serve(app, host="0.0.0.0", port=port)
    if query:
        query_lower = query.lower()
        movies = [m for m in movies if query_lower in m.title.lower() or query_lower in m.director.lower() or query_lower in m.genre.lower()]

    if genre:
        movies = [m for m in movies if m.genre.lower() == genre.lower()]

    genres = sorted({m.genre for m in db.movies})

    # ← NEW: Server-side admin check for template
    is_admin = check_auth()

    return render_template(
        "index.html",
        movies=movies,
        genres=genres,
        query=query,
        selected_genre=genre,
        is_admin=is_admin  # ← PASS THIS TO TEMPLATE
    )

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        flash("Movie not found!", "error")
        return redirect("/")
    
    # ← NEW: Server-side admin check for template
    is_admin = check_auth()
    
    return render_template("movie.html", movie=movie, is_admin=is_admin)  # ← PASS THIS TOO

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
                poster_url=request.form.get("poster_url", "").strip() or ""
            )
            db.movies.append(new_movie)
            flash("Movie added successfully!", "success")
            return redirect(url_for("movie_detail", movie_id=new_movie.id))
        except Exception as e:
            flash("Error adding movie.", "error")

    return render_template("add_movie.html")

@app.route("/movie/<int:movie_id>/review", methods=["POST"])
@requires_auth          # ← PROTECTED
def add_review(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        return redirect("/")

    author = request.form.get("author", "You").strip() or "You"
    text = request.form["text"].strip()
    rating = int(request.form["rating"])

    if text and 1 <= rating <= 5:
        movie.reviews.append(Review(author, text, rating))
        flash("Your review was added.", "success")
    else:
        flash("Invalid review.", "error")

    return redirect(url_for("movie_detail", movie_id=movie_id))

# ───── Server start (local + production) ─────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Waitress on port {port}...")
    serve(app, host="0.0.0.0", port=port)    
    return render_template("movie.html", movie=movie, is_admin=is_admin)  # ← PASS THIS TOO

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
                poster_url=request.form.get("poster_url", "").strip() or ""
            )
            db.movies.append(new_movie)
            flash("Movie added successfully!", "success")
            return redirect(url_for("movie_detail", movie_id=new_movie.id))
        except Exception as e:
            flash("Error adding movie.", "error")

    return render_template("add_movie.html")

@app.route("/movie/<int:movie_id>/review", methods=["POST"])
@requires_auth          # ← PROTECTED
def add_review(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        return redirect("/")

    author = request.form.get("author", "You").strip() or "You"
    text = request.form["text"].strip()
    rating = int(request.form["rating"])

    if text and 1 <= rating <= 5:
        movie.reviews.append(Review(author, text, rating))
        flash("Your review was added.", "success")
    else:
        flash("Invalid review.", "error")

    return redirect(url_for("movie_detail", movie_id=movie_id))

# ───── Server start (local + production) ─────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Waitress on port {port}...")
    serve(app, host="0.0.0.0", port=port)# app.py
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

    # ← NEW: Server-side admin check for template
    is_admin = check_auth()

    return render_template(
        "index.html",
        movies=movies,
        genres=genres,
        query=query,
        selected_genre=genre,
        is_admin=is_admin  # ← PASS THIS TO TEMPLATE
    )

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        flash("Movie not found!", "error")
        return redirect("/")
    
    # ← NEW: Server-side admin check for template
    is_admin = check_auth()
    
    return render_template("movie.html", movie=movie, is_admin=is_admin)  # ← PASS THIS TOO

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
                poster_url=request.form.get("poster_url", "").strip() or ""
            )
            db.movies.append(new_movie)
            flash("Movie added successfully!", "success")
            return redirect(url_for("movie_detail", movie_id=new_movie.id))
        except Exception as e:
            flash("Error adding movie.", "error")

    return render_template("add_movie.html")

@app.route("/movie/<int:movie_id>/review", methods=["POST"])
@requires_auth          # ← PROTECTED
def add_review(movie_id):
    movie = next((m for m in db.movies if m.id == movie_id), None)
    if not movie:
        return redirect("/")

    author = request.form.get("author", "You").strip() or "You"
    text = request.form["text"].strip()
    rating = int(request.form["rating"])

    if text and 1 <= rating <= 5:
        movie.reviews.append(Review(author, text, rating))
        flash("Your review was added.", "success")
    else:
        flash("Invalid review.", "error")

    return redirect(url_for("movie_detail", movie_id=movie_id))

# ───── Server start (local + production) ─────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
else:
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Waitress on port {port}...")
    serve(app, host="0.0.0.0", port=port)
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
