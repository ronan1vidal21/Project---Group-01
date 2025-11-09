from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app import models, db

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("/")
def get_leaderboard(database: Session = Depends(db.get_db)):
    users = database.query(models.User).order_by(models.User.points.desc()).limit(10).all()
    return [{"username": u.username, "points": u.points} for u in users]
