import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager

load_dotenv()

app = Flask(__name__)
data_manager = SQLiteDataManager('sqlite:///movieweb.db')


def fetch_movie_data(title):
    """
        Fetch movie details from OMDb API using the provided title.

        Args:
            title (str): The title of the movie to search for.

        Returns:
            dict or None: JSON data from OMDb if found, else None.
    """

    api_key = os.getenv('OMDB_API_KEY')
    url = f'http://www.omdbapi.com/?t={title}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


@app.route('/users')
def list_users():
    """
        Route to list all registered users.

        Returns:
            Rendered HTML template displaying user list.
    """

    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """
        Route to display a specific user's favorite movies.

        Args:
            user_id (int): The ID of the user.

        Returns:
            Rendered HTML page of that user's movies or 404 if user not found.
    """

    users = data_manager.get_all_users()
    user = next((u for u in users if u.id == user_id), None)

    if user is None:
        return f"User with ID {user_id} not found.", 404

    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
        Route to display and handle the form to add a new user.

        Returns:
            On GET: form to add user.
            On POST: redirect to /users after user is added.
    """

    if request.method == 'POST':
        user_name = request.form.get('name')
        if user_name:
            data_manager.add_user(user_name)
            return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
        Route to add a new movie for a user, using OMDb data.

        Args:
            user_id (int): The ID of the user.

        Returns:
            On GET: form to enter movie title.
            On POST: fetch movie from OMDb, add to DB, redirect to user_movies.
    """

    users = data_manager.get_all_users()
    user = next((u for u in users if u.id == user_id), None)
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            movie_data = fetch_movie_data(title)
            if movie_data and movie_data.get('Response') == 'True':
                data_manager.add_movie(
                    name=movie_data.get('Title'),
                    director=movie_data.get('Director'),
                    year=int(movie_data.get('Year', 0)),
                    rating=float(movie_data.get('imdbRating', 0)),
                    user_id=user_id
                )
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                return "Movie not found in OMDb.", 404

    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>',
           methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
        Route to update an existing movie's details.

        Args:
            user_id (int): The ID of the user who owns the movie.
            movie_id (int): The ID of the movie to update.

        Returns:
            On GET: pre-filled form with movie info.
            On POST: updated movie in DB, redirect to user's movie list.
    """

    users = data_manager.get_all_users()
    user = next((u for u in users if u.id == user_id), None)
    if not user:
        return "User not found", 404

    movies = data_manager.get_user_movies(user_id)
    movie = next((m for m in movies if m.id == movie_id), None)
    if not movie:
        return f"Movie with ID {movie_id} not found for user {user_id}.", 404

    if request.method == 'POST':
        new_name = request.form.get('name')
        new_director = request.form.get('director')
        new_year = request.form.get('year')
        new_rating = request.form.get('rating')

        data_manager.update_movie(
            movie_id=movie.id,
            name=new_name,
            director=new_director,
            year=int(new_year) if new_year else None,
            rating=float(new_rating) if new_rating else None
        )
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', user=user, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    """
        Route to delete a movie from the user's list.

        Args:
            user_id (int): The ID of the user.
            movie_id (int): The ID of the movie to delete.

        Returns:
            Redirect to user's movie list after deletion.
    """

    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == '__main__':
    app.run(debug=True)
