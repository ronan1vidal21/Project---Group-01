# backend/app/routers/plots.py
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app import crud
import matplotlib.pyplot as plt
import io
import pandas as pd
import sqlite3
import os

router = APIRouter(prefix="/plots", tags=["plots"])

@router.get("/user/{user_id}/points.png")
def user_points_plot(user_id: int, db: Session = Depends(get_db)):
    # Query action_records for user via raw SQL to produce a timeseries DataFrame
    db_url = db.bind.url if hasattr(db, "bind") else None
    # Use the same SQLite file used by SQLAlchemy engine
    engine = db.bind
    if engine is None:
        raise HTTPException(status_code=500, detail="DB engine not available")
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT created_at, points_awarded FROM action_records WHERE user_id = ? ORDER BY created_at",
            conn,
            params=[user_id],
            parse_dates=["created_at"]
        )
    if df.empty:
        # return a simple empty plot indicating no data
        fig, ax = plt.subplots(figsize=(6,3))
        ax.text(0.5, 0.5, "No actions logged yet", ha='center', va='center')
        ax.axis('off')
    else:
        df['cumulative'] = df['points_awarded'].cumsum()
        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(df['created_at'], df['cumulative'])
        ax.set_title("Cumulative Eco Points")
        ax.set_xlabel("Date")
        ax.set_ylabel("Points")
        fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")

