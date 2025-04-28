from abc import ABC, abstractmethod

"""
    Defines the abstract interface for data management operations.
    All concrete data managers (e.g., SQLite, JSON) must implement this interface.
"""


class DataManagerInterface(ABC):
    """
       Abstract base class for any data manager.
       Specifies the methods that all data manager classes must implement.
    """

    @abstractmethod
    def get_all_users(self):
        """Return a list of all users."""

        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """
            Return all movies belonging to the given user ID.

            Args:
                user_id (int): The ID of the user.
        """

        pass
