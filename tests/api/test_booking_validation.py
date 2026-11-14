import pytest

from data.factories import booking_payload

pytestmark = pytest.mark.api


def _error_fields(response) -> list:
    """Names of the fields the API reported as invalid."""
    return [detail["field"] for detail in response.json().get("details", [])]



# A6 | — | Quantity outside 1–10 is rejected
@pytest.mark.parametrize("quantity", [0, 11])
def test_quantity_outside_1_to_10_is_rejected(test_event, create_booking, quantity):
    response = create_booking(booking_payload(test_event["id"], quantity=quantity))

    assert response.status == 400, response.text()
    assert "quantity" in _error_fields(response)



# A7 | — | Invalid name, email or phone is rejected, naming the bad field
@pytest.mark.parametrize(
    "field, value",
    [
        ("customerName", "A"),
        ("customerEmail", "not-an-email"),
        ("customerPhone", "12345"),
        ("customerPhone", "abcdefghij"),
    ],
    ids=["name-too-short", "invalid-email", "phone-too-short", "phone-with-letters"],
)
def test_invalid_customer_data_is_rejected(test_event, create_booking, field, value):
    response = create_booking(booking_payload(test_event["id"], **{field: value}))

    assert response.status == 400, response.text()
    assert field in _error_fields(response)


# A7 | — | Missing required field is rejected, naming that field
def test_missing_required_field_is_rejected(test_event, create_booking):
    payload = booking_payload(test_event["id"])
    del payload["customerEmail"]

    response = create_booking(payload)

    assert response.status == 400, response.text()
    assert "customerEmail" in _error_fields(response)


# A8 | — | Booking more tickets than seats left is rejected
def test_booking_more_tickets_than_available_is_rejected(create_event, create_booking):
    event = create_event(totalSeats=2)

    response = create_booking(booking_payload(event["id"], quantity=3))

    assert response.status == 400, response.text()
    assert "2 seat(s) available" in response.json()["error"]


# A9 | — | Booking for a non-existent event returns 404
def test_booking_for_non_existent_event_returns_404(create_booking):
    response = create_booking(booking_payload(event_id=999_999_999))

    assert response.status == 404, response.text()