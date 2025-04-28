from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

"""
    Defines SQLAlchemy ORM models for User and Movie entities.
"""

Base = declarative_base()


class User(Base):
    """
        Represents a user in the system.

        Attributes:
            id (int): Primary key for the user.
            name (str): The user's name.
            movies (list[Movie]): One-to-many relationship to the user's added movies.
            reviews (list[Review]): One-to-many relationship to the user's written reviews.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    movies = relationship("Movie", back_populates="user", cascade="all, delete")
    reviews = relationship("Review", back_populates="user", cascade="all, delete")


class Movie(Base):
    """
        Represents a movie in the database.

        Attributes:
            id (int): Primary key for the movie.
            name (str): Movie title.
            director (str): Director's name.
            year (int): Release year.
            rating (float): IMDb-style rating.
            user_id (int): Foreign key to the user who added this movie.
            user (User): The user who added this movie.
            reviews (list[Review]): List of reviews written for this movie.
    """

    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    director = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    poster_url = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="movies")

    reviews = relationship("Review", back_populates="movie", cascade="all, delete")


class Review(Base):
    """
        Represents a review left by a user for a movie.

        Attributes:
            id (int): Primary key for the review.
            user_id (int): Foreign key to the reviewing user.
            movie_id (int): Foreign key to the reviewed movie.
            text (str): Text content of the review.
            rating (float): Star rating given to the movie (independent of IMDb rating).
            user (User): Relationship to the User who wrote the review.
            movie (Movie): Relationship to the Movie being reviewed.
    """

    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    text = Column(String)
    rating = Column(Float)

    user = relationship("User", back_populates="reviews")
    movie = relationship("Movie", back_populates="reviews")
