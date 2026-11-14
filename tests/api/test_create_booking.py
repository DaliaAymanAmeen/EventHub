import pytest

from data.factories import booking_payload
import re

pytestmark = pytest.mark.api

# A1 | AC1, AC5 | POST /bookings creates a confirmed booking with our data
@pytest.mark.smoke
def test_create_booking_returns_confirmed_booking(test_event, create_booking):
    payload = booking_payload(event_id=test_event["id"], quantity=2)

    response = create_booking(payload)
   
    assert response.status == 201, response.text()
    body = response.json()

    assert body["success"] is True

    booking = body["data"]
    assert booking["status"] == "confirmed"
    assert booking["eventId"] == test_event["id"]
    assert booking["quantity"] == 2
    assert booking["customerName"] == payload["customerName"]
    assert booking["customerEmail"] == payload["customerEmail"]
    assert booking["customerPhone"] == payload["customerPhone"]
    assert booking["bookingRef"], "Booking reference should not be empty"



# A12 | AC1 | Booking ref follows documented EVT-XXXXXX format (known bug)
@pytest.mark.xfail(
    reason="BUG: docs promise refs like 'EVT-A1B2C3', app returns refs like 'H-QCEQEM'",
    strict=True,
)
def test_booking_ref_matches_documented_format(test_event, create_booking):
    response = create_booking(booking_payload(test_event["id"]))

    assert response.status == 201, response.text()

    booking_ref = response.json()["data"]["bookingRef"]
    assert re.fullmatch(r"EVT-[A-Z0-9]{6}", booking_ref), f"Unexpected ref: {booking_ref}"


