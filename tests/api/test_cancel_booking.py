import pytest

from data.factories import booking_payload

pytestmark = pytest.mark.api

# A4 | AC4 | Cancelling removes the booking (API hard-deletes it)
def test_cancelled_booking_is_removed(booking, bookings_api, test_event):
    response = bookings_api.cancel(booking["id"])
    assert response.status == 200, response.text()
    assert response.json()["success"] is True

    # Cancel is a hard delete: the booking no longer exists
    assert bookings_api.get(booking["id"]).status == 404
    listing = bookings_api.list(eventId=test_event["id"], limit=100)
    assert booking["id"] not in [b["id"] for b in listing.json()["data"]]



# A5 | AC5 | Seats drop on booking and are restored on cancel
def test_seats_are_reserved_on_booking_and_released_on_cancel(
    create_event, create_booking, events_api, bookings_api
):
    event = create_event(totalSeats=20)

    def available_seats() -> int:
        return events_api.get(event["id"]).json()["data"]["availableSeats"]

    assert available_seats() == 20

    response = create_booking(booking_payload(event["id"], quantity=3))
    assert response.status == 201, response.text()
    assert available_seats() == 17

    bookings_api.cancel(response.json()["data"]["id"])
    assert available_seats() == 20



# A11 | AC4 | Cancelling a non-existent booking returns 404
def test_cancel_non_existent_booking_returns_404(bookings_api):
    response = bookings_api.cancel(999_999_999)
    assert response.status == 404, response.text()