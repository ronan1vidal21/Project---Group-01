from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app import db, models

router = APIRouter(
    prefix="/challenges",
    tags=["challenges"]
)

# Fallback static challenges (used if DB has none)
CHALLENGES = [
    {"title": "Ride 10 km by bike", "description": "Earn +50 points", "goal": 10, "reward_points": 50},
    {"title": "Plant 5 trees", "description": "Earn +25 points", "goal": 5, "reward_points": 25},
    {"title": "Use 10 reusable bags", "description": "Earn +20 points", "goal": 10, "reward_points": 20},
    {"title": "Recycle 20 plastics", "description": "Earn +40 points", "goal": 20, "reward_points": 40}
]


@router.get("/")
def get_challenges(username: str = None, db_session: Session = Depends(db.get_db)):
    """
    Returns all challenges with the current user's progress.
    If username is provided, reads progress from ChallengeProgress records.
    """
    user = None
    if username:
        user = db_session.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    db_challenges = db_session.query(models.Challenge).all()
    if not db_challenges:
        # DB not seeded  return fallback list with zero progress
        result = []
        for ch in CHALLENGES:
            result.append({
                "title": ch["title"],
                "description": ch["description"],
                "goal": ch["goal"],
                "progress": 0,
                "reward_points": ch["reward_points"]
            })
        return result

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
            "progress": progress_value,
            "reward_points": ch.reward_points
        })

    return challenges_with_progress

