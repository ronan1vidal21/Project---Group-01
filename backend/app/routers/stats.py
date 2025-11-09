from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app import db, models
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from fastapi.responses import Response

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/user/{username}/chart")
def user_points_chart(username: str, db_session: Session = Depends(db.get_db)):
    """
    Returns a PNG line chart of cumulative points over time for the given user.
    """
    user = db_session.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    actions = (
        db_session.query(models.ActionType)
        .filter(models.ActionType.user_id == user.id)
        .order_by(models.ActionType.timestamp)
        .all()
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    if not actions:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=14)
        ax.axis("off")
    else:
        times = [a.timestamp for a in actions]
        cumul = []
        total = 0
        for a in actions:
            total += (a.points or 0)
            cumul.append(total)

        ax.plot(times, cumul, marker="o", linestyle="-")
        ax.set_title(f"Cumulative Points  {user.username}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Points")
        fig.autofmt_xdate()
        ax.grid(True)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")
