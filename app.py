from flask import Flask
from flask_migrate import Migrate
from database import db    
from database.populate import PopulateDB
from routes.party import party_bp 
from routes.constituency import constituency_bp
from routes.candidate import candidate_bp
from routes.election import election_bp

app = Flask(__name__)

# Configure DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost/INDIA'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Register Blueprints
app.register_blueprint(party_bp, url_prefix='/api/v1') 
app.register_blueprint(constituency_bp, url_prefix='/api/v1')
app.register_blueprint(candidate_bp, url_prefix="/api/v1")
app.register_blueprint(election_bp, url_prefix="/api/v1")

# Init DB + Populate
def init_db():
    with app.app_context():
        print("Database initialized")

        populate = PopulateDB(db, app.config['SQLALCHEMY_DATABASE_URI'])  # ✅ Match this to your class definition
        populate.init_populate()
        print("Database populated")
