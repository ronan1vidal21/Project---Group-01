from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.services.carbon_service import estimate_emissions

router = APIRouter(prefix="/carbon", tags=["carbon"])


class CarbonEstimateRequest(BaseModel):
    action_name: str = Field(..., example="Rode a Bike")
    quantity: float = Field(..., example=1.0)


class CarbonEstimateResponse(BaseModel):
    co2_kg: float
    source: str
    detail: dict


@router.post("/estimate", response_model=CarbonEstimateResponse)
def estimate(req: CarbonEstimateRequest):
    if req.quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity must be non-negative")

    result = estimate_emissions(req.action_name, req.quantity)
    return result
