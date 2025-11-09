from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.db import Base, engine
from backend.app.routers import auth, actions, leaderboard, challenges, carbon, stats

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Eco Action Tracker API")

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(actions.router)
app.include_router(leaderboard.router)
app.include_router(challenges.router)
app.include_router(carbon.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {"message": "Eco Action Tracker API is running!"}