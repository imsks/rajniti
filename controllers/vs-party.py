import json
from database.models import PartyResults  
from utils.scraper import PartyScraper   
from database.db import db                

class PartyController:
    def __init__(self, config):
        self.config = config
        self.scraper = PartyScraper(config)
        self.json_file = "party_results.json"

    def scrape_data(self):
        url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
        return self.scraper.scrape(url)

    def verify_data(self):
        try:
            data = self.scraper.load_json(self.json_file)
            issues = []
            names = set()
            
            for idx, item in enumerate(data):
                # Check required fields
                if not all(key in item for key in ['party_name', 'symbol', 'total_seats']):
                    issues.append(f"Missing fields in record {idx+1}")
                    continue
                
                # Check duplicates
                if item['party_name'] in names:
                    issues.append(f"Duplicate party name: {item['party_name']}")
                names.add(item['party_name'])
                
                # Validate data types
                if not isinstance(item['total_seats'], int):
                    issues.append(f"Invalid seats format for {item['party_name']}")

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
                if not PartyResults.query.filter_by(party_name=item['party_name']).first():
                    party = PartyResults(
                        party_name=item['party_name'],
                        symbol=item['symbol'],
                        total_seats=item['total_seats']
                    )
                    db.session.add(party)
                    new_count += 1
            
            db.session.commit()
            
            return {
                "total_records": len(data),
                "new_records": new_count,
                "existing_records": len(data) - new_count
            }
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}
