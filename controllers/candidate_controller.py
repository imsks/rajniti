import json
import re
from app.database.models import candidate_Results
from utils.scraper import CandidateScraper

class CandidateController:
    def __init__(self, config):
        self.config = config
        self.scraper = CandidateScraper(config)
        self.js
        on_file = "candidate_results.json"

    def scrape_data(self, start=1, end=200):
        base_url = "https://results.eci.gov.in/ResultAcGenNov2024/"
        return self.scraper.scrape(base_url, start, end)

    def verify_data(self):
        try:
            data = self.scraper.load_json(self.json_file)
            issues = []
            candidates = set()
            
            for idx, item in enumerate(data):
                # Check required fields
                required_fields = ['constituency_code', 'name', 'party']
                if not all(key in item for key in required_fields):
                    issues.append(f"Missing fields in record {idx+1}")
                
                # Check duplicates
                candidate_key = f"{item['constituency_code']}-{item['name']}"
                if candidate_key in candidates:
                    issues.append(f"Duplicate candidate: {candidate_key}")
                candidates.add(candidate_key)
                
                # Validate votes format
                if item.get('votes') and not re.match(r'^\d+$', str(item['votes'])):
                    issues.append(f"Invalid votes format for {item['name']}")

            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "total_records": len(data)
            }
        except Exception as e:
            return {"error": str(e)}

    def insert_data(self):
        try:
            data = self.scraper.load_json(self.json_file)
            new_count = 0
            
            for item in data:
                if not candidate_Results.query.filter_by(
                    constituency_code=item['constituency_code'],
                    name=item['name']
                ).first():
                    candidate = candidate_Results(
                        constituency_code=item['constituency_code'],
                        name=item['name'],
                        party=item['party'],
                        status=item.get('status'),
                        votes=item.get('votes'),
                        margin=item.get('margin'),
                        image_url=item.get('image_url')
                    )
                    candidate.save()
                    new_count += 1
            
            return {
                "total_records": len(data),
                "new_records": new_count,
                "existing_records": len(data) - new_count
            }
        except Exception as e:
            return {"error": str(e)}