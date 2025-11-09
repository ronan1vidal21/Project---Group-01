# backend/app/services/scoring.py
from typing import Optional
from backend.app.models import ActionType

def compute_points(action_type: ActionType, distance_km: Optional[float]=0.0, metadata: dict=None) -> int:
    """
    Basic scoring formula:
      points = base_points + floor(distance_km * distance_factor) + bonus
    You can extend with frequency multipliers or carbon multipliers.
    """
    base = action_type.base_points or 0
    distance_factor = 1.0
    bonus = 0
    if distance_km and distance_km > 0:
        base += int(distance_km * distance_factor)
    # example bonus for tree planting or high-impact actions:
    if action_type.code == "plant_tree":
        bonus = 10
    return int(base + bonus)

