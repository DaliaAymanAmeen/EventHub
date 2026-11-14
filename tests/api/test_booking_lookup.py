import pytest

pytestmark = pytest.mark.api

# A3 | AC3 | Booking can be found by id, by reference and in the list
def test_booking_can_be_found_by_id_ref_and_in_list(booking, bookings_api, test_event):
    by_id = bookings_api.get(booking["id"])
    assert by_id.status == 200, by_id.text()
    assert by_id.json()["data"]["bookingRef"] == booking["bookingRef"]


    by_ref = bookings_api.get_by_ref(booking["bookingRef"])
    assert by_ref.status == 200, by_ref.text()
    assert by_ref.json()["data"]["id"] == booking["id"]

    listing = bookings_api.list(eventId=test_event["id"], limit=100)
    assert listing.status == 200, listing.text()
    listed_ids = [b["id"] for b in listing.json()["data"]]
    assert booking["id"] in listed_ids


    