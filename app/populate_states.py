from app import create_app
from database import db
from database.models import State

app = create_app()

with app.app_context():
    State.populate_states()
    print("States populated successfully.")
