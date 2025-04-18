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
            id (int): Primary key.
            name (str): User's name.
            movies (relationship): One-to-many relationship to Movie.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    movies = relationship("Movie", back_populates="user")


class Movie(Base):
    """
        Represents a movie in the user's collection.

        Attributes:
            id (int): Primary key.
            name (str): Movie title.
            director (str): Movie director.
            year (int): Year of release.
            rating (float): IMDb rating.
            user_id (int): Foreign key to User.
            user (relationship): Many-to-one relationship to User.
    """

    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    director = Column(String)
    year = Column(Integer)
    rating = Column(Float)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="movies")
