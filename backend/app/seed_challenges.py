from backend.app import models, db

def seed_challenges():
    database = db.SessionLocal()
    default_challenges = [
        {"title": "Ride 10 km by bike", "goal": 10, "reward_points": 50},
        {"title": "Plant 5 trees", "goal": 5, "reward_points": 25},
        {"title": "Use 10 reusable bags", "goal": 10, "reward_points": 20},
        {"title": "Recycle 20 plastics", "goal": 20, "reward_points": 40},
    ]

    for ch in default_challenges:
        existing = database.query(models.Challenge).filter_by(title=ch["title"]).first()
        if not existing:
            database.add(models.Challenge(**ch))

    database.commit()
    database.close()

if __name__ == "__main__":
    seed_challenges()

