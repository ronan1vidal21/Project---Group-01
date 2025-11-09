from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app import models, schemas, db

router = APIRouter(prefix="/actions", tags=["Actions"])


@router.post("/log")
def log_action(action: schemas.ActionLogRequest, database: Session = Depends(db.get_db)):
    user = database.query(models.User).filter(models.User.username == action.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate base points
    if action.action_name == "Rode a Bike":
        points = int(10 * action.quantity)
    elif action.action_name == "Planted a Tree":
        points = int(20 * action.quantity)
    elif action.action_name == "Used a Reusable Bag":
        points = int(5 * action.quantity)
    elif action.action_name == "Recycled Plastic":
        points = int(15 * action.quantity)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    # Log the base action
    new_action = models.ActionType(
        user_id=user.id,
        action_name=action.action_name,
        points=points
    )
    user.points += points
    database.add(new_action)
    database.commit()
    database.refresh(user)

    # --- Challenge tracking ---
    challenge_map = {
        "Rode a Bike": "Ride 10 km by bike",
        "Planted a Tree": "Plant 5 trees",
        "Used a Reusable Bag": "Use 10 reusable bags",
        "Recycled Plastic": "Recycle 20 plastics",
    }

    challenge_title = challenge_map.get(action.action_name)
    challenge = database.query(models.Challenge).filter(models.Challenge.title == challenge_title).first()

    if challenge:
        progress = (
            database.query(models.ChallengeProgress)
            .filter(
                models.ChallengeProgress.user_id == user.id,
                models.ChallengeProgress.challenge_id == challenge.id
            )
            .first()
        )

        if not progress:
            progress = models.ChallengeProgress(
                user_id=user.id,
                challenge_id=challenge.id,
                progress=0
            )
            database.add(progress)
            database.commit()

        progress.progress += action.quantity

        # Check completion
        if progress.progress >= challenge.goal:
            user.points += challenge.reward_points
            database.commit()
            return {
                "message": f"✅ Challenge '{challenge.title}' completed! +{challenge.reward_points} bonus points",
                "points": user.points,
                "progress": f"{challenge.goal}/{challenge.goal}",
            }

        database.commit()
        return {
            "message": f"Progress updated: {progress.progress}/{challenge.goal}",
            "points": user.points,
            "progress": f"{progress.progress}/{challenge.goal}",
        }

    return {"message": "✅ Action logged successfully", "points": user.points}
