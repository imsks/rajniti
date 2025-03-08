from app import create_app, db
from app.models import State

app = create_app()

with app.app_context():
    State.populate_states()
    
