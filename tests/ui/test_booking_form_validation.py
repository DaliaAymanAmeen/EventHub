import pytest
from playwright.sync_api import expect

from pages.event_details_page import EventDetailsPage

pytestmark = pytest.mark.ui

EXPECTED_ERRORS = [
    "Name must be at least 2 chars",
    "Enter a valid email",
    "Enter a valid 10-digit phone",
]


# U4 | — | Submitting the empty form shows an error for each field and books nothing
def test_empty_booking_form_shows_validation_errors(logged_in_page, create_event, bookings_api):
    event = create_event()

    event_page = EventDetailsPage(logged_in_page).open(event["id"])
    event_page.confirm()

    for message in EXPECTED_ERRORS:
        expect(event_page.validation_error(message)).to_be_visible()
    expect(event_page.confirmation_heading).to_have_count(0)

    bookings = bookings_api.list(eventId=event["id"])
    assert bookings.json()["pagination"]["total"] == 0