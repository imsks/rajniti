from database.models import db, State

class PopulateDB:
    def __init__(self, db):
        self.db = db

    def init_populate(self):
        """Populates the database with states."""
        states = [
            {"id": "AP", "name": "Andhra Pradesh"},
            {"id": "AR", "name": "Arunachal Pradesh"},
            {"id": "AS", "name": "Assam"},
            {"id": "BR", "name": "Bihar"},
            {"id": "CT", "name": "Chhattisgarh"},
            {"id": "GA", "name": "Goa"},
            {"id": "GJ", "name": "Gujarat"},
            {"id": "HR", "name": "Haryana"},
            {"id": "HP", "name": "Himachal Pradesh"},
            {"id": "JH", "name": "Jharkhand"},
            {"id": "KA", "name": "Karnataka"},
            {"id": "KL", "name": "Kerala"},
            {"id": "MP", "name": "Madhya Pradesh"},
            {"id": "MH", "name": "Maharashtra"},
            {"id": "MN", "name": "Manipur"},
            {"id": "ML", "name": "Meghalaya"},
            {"id": "MZ", "name": "Mizoram"},
            {"id": "NL", "name": "Nagaland"},
            {"id": "OD", "name": "Odisha"},
            {"id": "PB", "name": "Punjab"},
            {"id": "RJ", "name": "Rajasthan"},
            {"id": "SK", "name": "Sikkim"},
            {"id": "TN", "name": "Tamil Nadu"},
            {"id": "TG", "name": "Telangana"},
            {"id": "TR", "name": "Tripura"},
            {"id": "UP", "name": "Uttar Pradesh"},
            {"id": "UK", "name": "Uttarakhand"},
            {"id": "WB", "name": "West Bengal"},
            {"id": "AN", "name": "Andaman and Nicobar Islands"},
            {"id": "CH", "name": "Chandigarh"},
            {"id": "DN", "name": "Dadra and Nagar Haveli and Daman and Diu"},
            {"id": "DL", "name": "Delhi"},
            {"id": "JK", "name": "Jammu and Kashmir"},
            {"id": "LA", "name": "Ladakh"},
            {"id": "LD", "name": "Lakshadweep"},
            {"id": "PY", "name": "Puducherry"}
        ]

        try:
            for state in states:
                if not State.query.filter_by(id=state["id"]).first():
                    self.db.session.add(State(id=state["id"], name=state["name"]))

            self.db.session.commit()
            print("State table populated successfully.")
        except Exception as e:
            self.db.session.rollback()
            print(f"Error populating states: {str(e)}")
