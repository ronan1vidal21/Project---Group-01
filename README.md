# Eco Action Tracker

## Quickstart (development)

1. Create a virtual environment and install backend dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt

2. Load the challenges

py -m backend.app.seed_challenges

3. Load the Carbon API key
$env:CARBON_INTERFACE_API_KEY = "MwGFZymIcoW5mHN8SUhMhQ"

4. Start the backend
uvicorn backend.app.main:app --reload

5. Run the app.py
py app.py

Note: To remove the database file
rm eco_action_tracker.db

