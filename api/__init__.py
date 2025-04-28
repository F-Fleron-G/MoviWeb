from flask import Blueprint, jsonify, request
from datamanager.sqlite_data_manager import SQLiteDataManager
from models import Movie, Review


api = Blueprint('api', __name__)
data_manager = SQLiteDataManager()


@api.route('/users', methods=['GET'])
def get_users():
    users = data_manager.get_all_users()
    user_list = [{'id': user.id, 'name': user.name} for user in users]
    return jsonify(user_list)


@api.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    user = next((u for u in data_manager.get_all_users() if u.id == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    movies = data_manager.get_user_movies(user_id)
    movie_list = [{
        'id': m.id,
        'name': m.name,
        'director': m.director,
        'year': m.year,
        'rating': m.rating
    } for m in movies]

    return jsonify(movie_list)


@api.route('/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    user = next((u for u in data_manager.get_all_users() if u.id == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    required_fields = ['name', 'director', 'year', 'rating']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing movie data'}), 400

    new_movie = data_manager.add_movie(
        name=data['name'],
        director=data['director'],
        year=int(data['year']),
        rating=float(data['rating']),
        user_id=user_id
    )

    return jsonify({
        'message': 'Movie added successfully',
        'movie_id': new_movie.id
    }), 201


@api.route('/users/<int:user_id>/movies/<int:movie_id>', methods=['DELETE'])
def delete_user_movie(user_id, movie_id):
    user = next((u for u in data_manager.get_all_users() if u.id == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    movies = data_manager.get_user_movies(user_id)
    movie = next((m for m in movies if m.id == movie_id), None)
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404

    session = data_manager.Session()
    try:
        session.delete(movie)
        session.commit()
        return jsonify({'message': f"Movie '{movie.name}' deleted successfully."}), 200
    finally:
        session.close()


@api.route('/movies/<int:movie_id>/reviews', methods=['GET'])
def get_movie_reviews(movie_id):
    session = data_manager.Session()
    try:
        movie = session.query(Movie).filter_by(id=movie_id).first()
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404

        review_list = [{
            'id': review.id,
            'user_id': review.user_id,
            'text': review.text,
            'rating': review.rating
        } for review in movie.reviews]

        return jsonify(review_list)
    finally:
        session.close()


@api.route('/reviews', methods=['POST'])
def create_review():
    data = request.get_json()

    required_fields = ['user_id', 'movie_id', 'text', 'rating']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing review data'}), 400

    session = data_manager.Session()
    try:
        user = session.query(Movie).filter_by(id=data['movie_id']).first()
        movie = session.query(Movie).filter_by(id=data['movie_id']).first()
        if not user or not movie:
            return jsonify({'error': 'Invalid user or movie ID'}), 404

        new_review = Review(
            user_id=int(data['user_id']),
            movie_id=int(data['movie_id']),
            text=data['text'].strip(),
            rating=float(data['rating'])
        )

        session.add(new_review)
        session.commit()

        return jsonify({
            'message': 'Review created successfully',
            'review_id': new_review.id
        }), 201
    finally:
        session.close()


@api.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review_api(review_id):
    session = data_manager.Session()
    try:
        review = session.query(Review).filter_by(id=review_id).first()
        if not review:
            return jsonify({'error': 'Review not found'}), 404

        session.delete(review)
        session.commit()
        return jsonify({'message': 'Review deleted successfully.'}), 200
    finally:
        session.close()
