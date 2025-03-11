import json
from app.database.models import constituency_Results
from utils.scraper import ConstituencyScraper

class ConstituencyController:
    def __init__(self, config):
        self.config = config
        self.scraper = ConstituencyScraper(config)
        self.json_file = "constituency_results.json"

    def scrape_data(self):
        url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
        return self.scraper.scrape(url)

    def verify_data(self):
        try:
            data = self.scraper.load_json(self.json_file)
            issues = []
            ids = set()
            
            for idx, item in enumerate(data):
                # Check required fields
                required_fields = ['constituency_id', 'constituency_name', 'state_id']
                if not all(key in item for key in required_fields):
                    issues.append(f"Missing fields in record {idx+1}")
                
                # Check duplicates
                if item['constituency_id'] in ids:
                    issues.append(f"Duplicate constituency ID: {item['constituency_id']}")
                ids.add(item['constituency_id'])
                
                # Validate data types
                if not isinstance(item['constituency_id'], str):
                    issues.append(f"Invalid ID format for {item['constituency_name']}")

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
                if not constituency_Results.query.filter_by(constituency_id=item['constituency_id']).first():
                    constituency = constituency_Results(
                        constituency_id=item['constituency_id'],
                        constituency_name=item['constituency_name'],
                        state_id=item['state_id']
                    )
                    constituency.save()
                    new_count += 1
            
            return {
                "total_records": len(data),
                "new_records": new_count,
                "existing_records": len(data) - new_count
            }
        except Exception as e:
            return {"error": str(e)}
