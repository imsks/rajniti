from flask import Flask, jsonify, abort
import json
import os

app = Flask(__name__)

# Path to the scraped JSON file (replace this path with your actual file path)
data_file = "VS_election.json"


def load_data():
    """Load the scraped data from the JSON file."""
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return None


@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """API route to fetch all candidate data."""
    data = load_data()
    if data:
        return jsonify(data)
    else:
        abort(404, description="Data not found")


@app.route('/api/candidate/<constituency_code>', methods=['GET'])
def get_candidate_by_constituency(constituency_code):
    """API route to fetch data for a specific candidate by constituency code."""
    data = load_data()
    if data:
        candidate = next((item for item in data if item['Constituency Code'] == constituency_code), None)
        if candidate:
            return jsonify(candidate)
        else:
            abort(404, description="Candidate not found")
    else:
        abort(404, description="Data not found")


@app.errorhandler(404)
def not_found(error):
    """Custom error handler for 404 errors."""
    return jsonify({'error': str(error)}), 404


if __name__ == '__main__':
    app.run(debug=True)
