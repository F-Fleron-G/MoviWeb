from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from models import Base, User, Movie
from datamanager.data_manager_interface import DataManagerInterface

"""
    Concrete implementation of the DataManagerInterface using SQLite and SQLAlchemy.
    Handles all CRUD operations on users and movies.
"""


class SQLiteDataManager(DataManagerInterface):
    """
        SQLite implementation of the DataManagerInterface using SQLAlchemy ORM.
    """
    def __init__(self, db_path="sqlite:///movieweb.db"):
        """Initialize database engine and session factory."""

        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_all_users(self):
        """Retrieve all users from the database."""

        session = self.Session()
        try:
            user_list = session.query(User).all()
            return user_list
        finally:
            session.close()

    def get_user_movies(self, user_id):
        """
            Retrieve all movies associated with a specific user.

            Args:
                user_id (int): The user's ID.
        """

        session = self.Session()
        try:
            movies = session.query(Movie).filter(and_(Movie.user_id == user_id)).all()
            return movies
        finally:
            session.close()

    def add_user(self, user_name):
        """
            Add a new user to the database.

            Args:
                user_name (str): Name of the user to add.
        """

        session = self.Session()
        try:
            new_user = User(name=user_name)
            session.add(new_user)
            session.commit()
            return new_user
        finally:
            session.close()

    def add_movie(self, name, director, year, rating, user_id):
        """
           Add a new movie to a user's movie list.

           Args:
               name (str): Movie title.
               director (str): Director's name.
               year (int): Year of release.
               rating (float): Movie rating.
               user_id (int): ID of the user.
        """

        session = self.Session()
        try:
            new_movie = Movie(
                name=name,
                director=director,
                year=year,
                rating=rating,
                user_id=user_id
            )
            session.add(new_movie)
            session.commit()
            return new_movie
        finally:
            session.close()

    def update_movie(self, movie_id, name=None, director=None, year=None, rating=None):
        """
            Update movie details in the database.

            Args:
                movie_id (int): The ID of the movie to update.
                name (str, optional): New title.
                director (str, optional): New director.
                year (int, optional): New release year.
                rating (float, optional): New rating.
        """

        session = self.Session()
        try:
            movie = session.query(Movie).filter(and_(Movie.id == movie_id)).first()
            if not movie:
                return None

            if name is not None:
                movie.name = name
            if director is not None:
                movie.director = director
            if year is not None:
                movie.year = year
            if rating is not None:
                movie.rating = rating

            session.commit()
            return movie
        finally:
            session.close()

    def delete_movie(self, movie_id):
        """
            Delete a movie from the database.

            Args:
                movie_id (int): The ID of the movie to delete.

            Returns:
                bool: True if deletion succeeded, False if movie not found.
        """

        session = self.Session()
        try:
            movie = session.query(Movie).filter(and_(Movie.id == movie_id)).first()
            if not movie:
                return False

            session.delete(movie)
            session.commit()
            return True
        finally:
            session.close()
