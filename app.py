import os
import requests
from dotenv import load_dotenv
from api import api
from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.sqlite_data_manager import SQLiteDataManager
from models import Review


load_dotenv()

app = Flask(__name__)
data_manager = SQLiteDataManager('sqlite:///movieweb.db')

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-mode-fallback-key")


def get_user(user_id):
    """
        Helper function to fetch a user by ID from the data manager.

        Args:
            user_id (int): The user's ID.

        Returns:
            User object if found, None otherwise.
    """
    return next((u for u in data_manager.get_all_users() if u.id == user_id), None)


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


@app.route('/')
def home():
    """
        Welcome splash screen for MovieWeb.
    """

    return render_template('home.html')


@app.route('/admin')
def admin_panel():
    """
        Admin panel to view and search all users and manage deletions.
    """

    query = request.args.get('q', '').strip().lower()
    users = sorted(data_manager.get_all_users(), key=lambda u: u.name.lower())

    if query:
        users = [user for user in users if query in user.name.lower()]

    return render_template('admin.html', users=users, query=query)


@app.route('/users')
def list_users():
    """
        Route to list all users, with optional search filter.
    """

    query = request.args.get('q', '').strip().lower()
    users = sorted(data_manager.get_all_users(), key=lambda u: u.name.lower())

    if query:
        users = [user for user in users if query in user.name.lower()]

    return render_template('users.html', users=users, query=query)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """
        Route to display a specific user's favorite movies.

        Args:
            user_id (int): The ID of the user.

        Returns:
            Rendered HTML page of that user's movies or 404 if user not found.
    """

    user = get_user(user_id)

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
        raw_name = request.form.get('name')

        if raw_name:
            cleaned_name = raw_name.strip().title()

            if not cleaned_name.replace(" ", "").isalpha():
                flash("Invalid characters in name. Use letters and spaces only.", "error")
                return redirect(url_for('add_user'))

            data_manager.add_user(cleaned_name)
            flash(f"User '{cleaned_name}' added successfully!", "success")
            return redirect(url_for('list_users'))

    return render_template('add_user.html')


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    """
        Route to delete a user and their associated movies.
    """

    data_manager.delete_user(user_id)
    flash("User deleted.", "success")
    return redirect(url_for('list_users'))


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

    user = get_user(user_id)

    if not user:
        return "User not found", 404

    if request.method == 'POST':
        title = request.form.get('title', '').strip().title()
        if title:
            try:
                movie_data = fetch_movie_data(title)
                name = movie_data.get('Title', '').strip().title()
                director = movie_data.get('Director', '').strip().title()
                poster_url = movie_data.get('Poster')

                if movie_data and movie_data.get('Response') == 'True':
                    data_manager.add_movie(
                        name=name,
                        director=director,
                        year=int(movie_data.get('Year', 0)),
                        rating=float(movie_data.get('imdbRating', 0)),
                        user_id=user_id,
                        poster_url=poster_url
                    )
                    flash(f"Movie '{name}' added for {user.name}!", "success")
                    return redirect(url_for('user_movies', user_id=user_id))
                else:
                    flash("Movie not found in OMDb.", "error")
                    return redirect(url_for('add_movie', user_id=user_id))
            except Exception as e:
                return f"An error occurred while adding the movie: {str(e)}", 500

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

    user = get_user(user_id)

    if not user:
        return "User not found", 404

    movies = data_manager.get_user_movies(user_id)
    movie = next((m for m in movies if m.id == movie_id), None)
    if not movie:
        return f"Movie with ID {movie_id} not found for user {user_id}.", 404

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip().title()
        new_director = request.form.get('director', '').strip().title()
        new_year = request.form.get('year')
        new_rating = request.form.get('rating')

        data_manager.update_movie(
            movie_id=movie.id,
            name=new_name,
            director=new_director,
            year=int(new_year) if new_year else None,
            rating=float(new_rating) if new_rating else None
        )
        flash(f"Movie '{new_name}' updated successfully!", "success")
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', user=user, movie=movie)


@app.route('/users/<int:user_id>/review/<int:movie_id>', methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    """
        Route to add a review for a movie by a specific user.
    """

    user = get_user(user_id)
    movie = next((m for m in data_manager.get_user_movies(user_id) if m.id == movie_id), None)

    if not user or not movie:
        flash("User or movie not found.", "error")
        return redirect(url_for('list_users'))

    if request.method == 'POST':
        review_text = request.form.get('review', '').strip()
        rating = request.form.get('rating')

        try:
            rating = float(rating)
        except (ValueError, TypeError):
            flash("Invalid rating. Please enter a number.", "error")
            return redirect(request.url)

        session = data_manager.Session()
        try:
            new_review = Review(
                user_id=user.id,
                movie_id=movie.id,
                text=review_text,
                rating=rating
            )
            session.add(new_review)
            session.commit()
            flash("Review added successfully!", "success")
        finally:
            session.close()

        return redirect(url_for('user_movies', user_id=user.id))

    return render_template('add_review.html', user=user, movie=movie)


@app.route('/users/<int:user_id>/review/<int:movie_id>/edit', methods=['GET', 'POST'])
def edit_review(user_id, movie_id):
    """
        Route to update an existing review for a specific user/movie.
    """

    user = get_user(user_id)
    movie = next((m for m in data_manager.get_user_movies(user_id) if m.id == movie_id), None)

    if not user or not movie:
        flash("User or movie not found.", "error")
        return redirect(url_for('list_users'))

    session = data_manager.Session()
    try:
        review = session.query(Review).filter_by(user_id=user.id, movie_id=movie.id).first()
        if not review:
            flash("Review not found.", "error")
            return redirect(url_for('user_movies', user_id=user.id))

        if request.method == 'POST':
            review.text = request.form.get('review', '').strip()
            try:
                review.rating = float(request.form.get('rating'))
            except (ValueError, TypeError):
                flash("Invalid rating.", "error")
                return redirect(request.url)

            session.commit()
            flash("Review updated successfully!", "success")
            return redirect(url_for('user_movies', user_id=user.id))

    finally:
        session.close()

    return render_template('edit_review.html', user=user, movie=movie, review=review)


@app.route('/users/<int:user_id>/review/<int:movie_id>/delete')
def delete_review(user_id, movie_id):
    """
        Route to delete a review for a movie by a specific user.
    """

    session = data_manager.Session()
    try:
        review = session.query(Review).filter_by(user_id=user_id, movie_id=movie_id).first()
        if review:
            session.delete(review)
            session.commit()
            flash("Review deleted successfully.", "success")
        else:
            flash("Review not found.", "error")
    finally:
        session.close()

    return redirect(url_for('user_movies', user_id=user_id))


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
    flash("Movie deleted.", "success")
    return redirect(url_for('user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    """
        Custom handler for 404 Not Found errors.

        Returns:
            A rendered 404.html page with a 404 status code.
    """

    return render_template('404.html'), 404


app.register_blueprint(api, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)
