
import os
import requests
from typing import Dict, Any

# Small, human-readable fallback emission factors (kg CO2 per unit)
_FALLBACK_FACTORS = {
    "Rode a Bike": {"per_km": -0.05},            # negative = approximate saving vs driving (kg CO2 per km)
    "Planted a Tree": {"per_tree": -21.77},      # approximate sequestration per year (kg CO2)  illustrative
    "Used a Reusable Bag": {"per_bag": -0.01},   # tiny per-use saving (kg CO2)  illustrative
    "Recycled Plastic": {"per_item": -0.2},      # approximate saving per plastic item (kg CO2)
}

CARBON_INTERFACE_KEY = os.getenv("CARBON_INTERFACE_API_KEY")  # optional real API key


def _approximate_estimate(action_name: str, quantity: float) -> Dict[str, Any]:
    """Return a best-effort local approximation (kg CO2) and metadata."""
    action = _FALLBACK_FACTORS.get(action_name, {})
    co2 = 0.0
    detail = {}

    if action_name == "Rode a Bike":
        per = action.get("per_km", -0.05)
        co2 = per * quantity
        detail = {"unit": "km", "factor_kg_co2_per_unit": per}
    elif action_name == "Planted a Tree":
        per = action.get("per_tree", -21.77)
        co2 = per * quantity
        detail = {"unit": "tree", "factor_kg_co2_per_unit": per}
    elif action_name == "Used a Reusable Bag":
        per = action.get("per_bag", -0.01)
        co2 = per * quantity
        detail = {"unit": "bag", "factor_kg_co2_per_unit": per}
    elif action_name == "Recycled Plastic":
        per = action.get("per_item", -0.2)
        co2 = per * quantity
        detail = {"unit": "item", "factor_kg_co2_per_unit": per}
    else:
        # Generic conservative estimate (assume neutral)
        co2 = 0.0
        detail = {"note": "no fallback factor for this action"}

    return {
        "co2_kg": round(co2, 4),
        "source": "approximate-local",
        "detail": detail,
    }


def estimate_emissions(action_name: str, quantity: float) -> Dict[str, Any]:
    """
    Try to call an external carbon API when configured; otherwise return an approximate local estimate.
    - Set CARBON_INTERFACE_API_KEY in the environment to enable an external provider.
    - This function returns a dict with keys: co2_kg, source, detail.
    """
    # If a real API key is configured, attempt to call a provider (placeholder).
    # Here we only include the wiring; you can adapt to Climatiq/Carbon Interface per their docs.
    if CARBON_INTERFACE_KEY:
        try:
            # Example placeholder for Carbon Interface (adapt body to provider docs)
            url = "https://www.carboninterface.com/api/v1/estimates"
            headers = {
                "Authorization": f"Bearer {CARBON_INTERFACE_KEY}",
                "Content-Type": "application/json",
            }

            # Build a minimal estimate payload depending on action
            if action_name == "Rode a Bike":
                payload = {"type": "distance", "distance": {"value": float(quantity), "unit": "km"}}
            elif action_name == "Recycled Plastic":
                payload = {"type": "waste", "weight": {"value": float(quantity), "unit": "kg"}}
            else:
                payload = {"type": "misc", "quantity": float(quantity)}

            resp = requests.post(url, json=payload, headers=headers, timeout=8.0)
            resp.raise_for_status()
            data = resp.json()

            # Map provider response to our shape  provider shapes differ; adapt as needed.
            # Try common places for carbon mass values
            co2 = None
            if isinstance(data, dict):
                # Carbon Interface returns 'data' -> 'attributes' -> 'carbon_mt' sometimes
                if "data" in data and isinstance(data["data"], dict):
                    attrs = data["data"].get("attributes", {})
                    co2 = attrs.get("carbon_kg") or attrs.get("carbon_g")
                    if co2 and attrs.get("carbon_g"):
                        co2 = attrs.get("carbon_g") / 1000.0

            if co2 is None:
                # Fallback to local estimate if provider response unexpected
                return _approximate_estimate(action_name, quantity)

            return {
                "co2_kg": round(float(co2), 4),
                "source": "carbon-interface",
                "detail": {"raw": data},
            }
        except Exception:
            # On any error, fall back to approximate local calculation
            return _approximate_estimate(action_name, quantity)

    # No external key: return approximate estimate
    return _approximate_estimate(action_name, quantity)