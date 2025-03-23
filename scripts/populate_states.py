import traceback
from flask import Flask
from flask_migrate import Migrate
from database.models import db, State
from database.populate import PopulateDB  

app = Flask(__name__)

#  Database Configuration

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost/INDIA'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db.init_app(app)
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        print(" Running Database Migrations...")
        db.create_all()  # Ensures tables exist before migration

        print(" Database Initialized.")

        # Populate Database
        try:
            print(" Populating States...")
            State.populate_states()
            print("States Populated Successfully.")
        except Exception as e:
            db.session.rollback()
            print(" Error Populating Database:", str(e))
            traceback.print_exc()

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print("Error:", str(e))
        traceback.print_exc()
