from datamanager.sqlite_data_manager import SQLiteDataManager

db = SQLiteDataManager()
users = db.get_all_users()

for user in users:
    print(f"ID: {user.id}, Name: {user.name}")


new_user = db.add_user("Freddy")
print(f"Added user: ID={new_user.id}, Name={new_user.name}")


new_movie = db.add_movie(
    name="Interstellar",
    director="Christopher Nolan",
    year=2014,
    rating=8.6,
    user_id=1
)

print(f"Added movie: {new_movie.name} ({new_movie.year}) by {new_movie.director}")

updated_movie = db.update_movie(
    movie_id=1,
    name="Interstellar (Updated)",
    rating=9.0
)

if updated_movie:
    print(f"Updated movie: {updated_movie.name}, Rating: {updated_movie.rating}")
else:
    print("Movie not found.")

was_deleted = db.delete_movie(movie_id=1)

if was_deleted:
    print("Movie deleted successfully.")
else:
    print("Movie not found.")
