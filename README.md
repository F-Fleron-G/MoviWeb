# MoviWeb

MoviWeb is a Flask-based web application for managing users and their favorite movies. It allows you to add, view, update and delete users and their movie collections, fetch movie details via the OMDb API, and manage user reviews.

## Features

- **User management**  
  - Add new users  
  - List and search existing users  
  - Delete users  
- **Movie management**  
  - Add movies with details fetched from OMDb API  
  - View a user’s favorite movies  
  - Update movie details (title, director, year, rating)  
  - Delete movies  
- **Reviews**  
  - Add, edit and delete text reviews with star ratings (0–10 scale)  
- **Admin panel** for bulk user management  
- **Responsive UI** with light/dark theme toggle  

## Requirements

- Python 3.8 or higher  
- Git  
- An OMDb API key (register at http://www.omdbapi.com/)  

All Python dependencies are listed in `requirements.txt`.

## Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/F-Fleron-G/MoviWeb.git
   cd MoviWeb

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   .venv\Scripts\activate       # Windows

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   
4. **Configure environment variables**

   Create a file named .env in the project root with these entries:
   ```bash
   FLASK_SECRET_KEY=your_secret_key
   OMDB_API_KEY=your_omdb_api_key

5. **Initialize the database**

   The SQLite database (movieweb.db) will be created automatically on first run.


6. **Run the application**
   ```bash
   flask run or python3 app.py

Then open your browser at http://127.0.0.1:5000.
   
## Project Structure
   ```cssharp
    MoviWeb/
    ├── app.py
    ├── api/                 
    ├── datamanager/
    │   ├── data_manager_interface.py
    │   └── sqlite_data_manager.py
    ├── models.py
    ├── static/
    │   ├── images/
    │   └── styles.css
    ├── templates/
    │   ├── base.html
    │   ├── home.html
    │   ├── users.html
    │   └── … (other templates)
    ├── .env
    ├── requirements.txt
    └── README.md
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Have a fix or a feature to add? Feel free to submit a Pull Request. 
For any large changes, please open an issue first to discuss.
