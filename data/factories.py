import uuid
from datetime import datetime, timedelta, timezone


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def new_customer() -> dict:
    uid = unique_suffix()
    return {
        "customerName": f"QA Tester {uid}",
        "customerEmail": f"qa.{uid}@example.com",
        "customerPhone": "9876543210",
    }


def booking_payload(event_id: int, quantity: int = 1, **overrides) -> dict:
    payload = {"eventId": event_id, "quantity": quantity, **new_customer()}
    payload.update(overrides)
    return payload


def event_payload(**overrides) -> dict:
    event_date = datetime.now(timezone.utc) + timedelta(days=30)
    payload = {
        "title": f"QA Auto Event {unique_suffix()}",
        "description": "Created by automated tests. Safe to delete.",
        "category": "Workshop",
        "venue": "QA Test Venue",
        "city": "Pune",
        "eventDate": event_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "price": 99.99,
        "totalSeats": 100,
    }
    payload.update(overrides)
    return payload