from typing import List, Dict, Any


def rank_trips_by_efficiency(trips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return trips ranked by a simple efficiency score.

    Efficiency is defined as higher average speed and lower fare per km.
    The score combines normalized speed and inverse fare per km.
    Input items are expected to contain keys: trip_id, trip_distance_km,
    trip_duration_min, and optionally fare_amount.
    """
    ranked: List[Dict[str, Any]] = []

    for trip in trips:
        distance_km = _to_float(trip.get("trip_distance_km"))
        duration_min = _to_float(trip.get("trip_duration_min"))
        fare_amount = _to_float(trip.get("fare_amount"))

        if distance_km is None or duration_min is None or duration_min <= 0:
            continue

        hours = duration_min / 60.0
        speed_kmh = distance_km / hours if hours > 0 else 0.0
        fare_per_km = (fare_amount / distance_km) if (fare_amount is not None and distance_km > 0) else None

        capped_speed = max(0.0, min(speed_kmh, 120.0))
        norm_speed = capped_speed / 120.0

        if fare_per_km is None or fare_per_km <= 0:
            inv_fare_component = 0.5
        else:
            capped_fare_per_km = max(0.5, min(fare_per_km, 10.0))
            inv_fare_component = (10.0 - capped_fare_per_km) / 9.5

        score = 0.6 * norm_speed + 0.4 * inv_fare_component

        trip_with_score = dict(trip)
        trip_with_score["speed_kmh"] = speed_kmh
        if fare_per_km is not None:
            trip_with_score["fare_per_km"] = fare_per_km
        trip_with_score["efficiency_score"] = score
        ranked.append(trip_with_score)

    ranked.sort(key=lambda t: t.get("efficiency_score", 0.0), reverse=True)
    return ranked


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


