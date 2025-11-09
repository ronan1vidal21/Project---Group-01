from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app import db, models

router = APIRouter(
    prefix="/challenges",
    tags=["challenges"]
)

# Fallback static challenges for cases where DB isn't seeded yet
CHALLENGES = [
    {"title": "Ride 10 km by bike", "description": "Earn +50 points", "action": "Rode a Bike", "goal": 10},
    {"title": "Plant 5 trees", "description": "Earn +25 points", "action": "Planted a Tree", "goal": 5},
    {"title": "Use 10 reusable bags", "description": "Earn +20 points", "action": "Used a Reusable Bag", "goal": 10},
    {"title": "Recycle 20 plastics", "description": "Earn +40 points", "action": "Recycled Plastic", "goal": 20}
]


@router.get("/")
def get_challenges(username: str = None, db_session: Session = Depends(db.get_db)):
    """
    Returns all challenges with the current user's progress.
    If username is provided, reads real progress from ChallengeProgress records.
    """

    user = None
    if username:
        user = db_session.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    # Prefer challenges from DB (seeded). Fallback to static CHALLENGES if DB has none.
    db_challenges = db_session.query(models.Challenge).all()
    if not db_challenges:
        # Return static list (progress only available when username is provided)
        challenges_with_progress = []
        for ch in CHALLENGES:
            progress = 0
            challenges_with_progress.append({
                "title": ch["title"],
                "description": ch["description"],
                "goal": ch["goal"],
                "progress": progress
            })
        return challenges_with_progress

    # Build response using DB challenges and user-specific progress if available
    challenges_with_progress = []
    for ch in db_challenges:
        progress_value = 0
        if user:
            prog = (
                db_session.query(models.ChallengeProgress)
                .filter(
                    models.ChallengeProgress.user_id == user.id,
                    models.ChallengeProgress.challenge_id == ch.id
                )
                .first()
            )
            if prog:
                progress_value = prog.progress

        challenges_with_progress.append({
            "title": ch.title,
            "description": f"Earn +{ch.reward_points} points",
            "goal": ch.goal,
            "progress": progress_value
        })

    return challenges_with_progress