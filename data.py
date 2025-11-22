# data.py
from datetime import datetime
from typing import List, Optional

class Movie:
    _id_counter = 1

    def __init__(self, title: str, year: int, genre: str, director: str, poster_url: str = "", description: str = ""):
        self.id = Movie._id_counter
        Movie._id_counter += 1
        self.title = title
        self.year = year
        self.genre = genre
        self.director = director
        self.poster_url = poster_url or f"https://via.placeholder.com/300x450?text={title.replace(' ', '+')}"
        self.description = description
        self.reviews: List[Review] = []
        self.created_at = datetime.now()

    def average_rating(self) -> float:
        if not self.reviews:
            return 0.0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

class Review:
    def __init__(self, author: str, text: str, rating: int):
        self.author = author
        self.text = text
        self.rating = rating  # 1–5
        self.date = datetime.now().strftime("%B %d, %Y")

class Database:
    def __init__(self):
        self.movies: List[Movie] = []
        self._seed_data()

    def _seed_data(self):
        # Sample movies
        inception = Movie(
            title="Inception", year=2010, genre="Sci-Fi", director="Christopher Nolan",
            description="A thief who steals corporate secrets through dream-sharing technology...",
            poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/9gk7adHYeDkXNK0kuA7cfg5i9f8.jpg"
        )
        inception.reviews = [
            Review("Alice", "Mind-bending masterpiece!", 5),
            Review("Bob", "Confusing but brilliant", 4)
        ]

        dune = Movie("Dune: Part Two", year=2024, genre="Sci-Fi", director="Denis Villeneuve",
                     poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
                     description="Paul Atreides unites with the Fremen...")
        dune.reviews.append(Review("Cinephile", "Visually stunning epic", 5))

        self.movies.extend([inception, dune,
            Movie("The Shawshank Redemption", 1994, "Drama", "Frank Darabont",
                  poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"),
            Movie("Oppenheimer", 2023, "Biography", "Christopher Nolan",
                  poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg")
        ])

    def search(self, query: str) -> List[Movie]:
        query = query.lower()
        return [m for m in self.movies if query in m.title.lower() or query in m.director.lower() or query in m.genre.lower()]

db = Database()  # Singleton instance