import pytest
from playwright.sync_api import expect

from data.factories import booking_payload, new_customer
from pages.event_details_page import EventDetailsPage
from pages.my_bookings_page import MyBookingsPage

pytestmark = pytest.mark.ui


# U2 | AC3 | Booking made in the UI appears in My Bookings with the same reference
def test_booking_appears_in_my_bookings(logged_in_page, test_event, cleanup_ui_bookings):
    quantity = 2
    event_page = EventDetailsPage(logged_in_page).open(test_event["id"])
    event_page.book(new_customer(), quantity=quantity)
    expect(event_page.confirmation_heading).to_be_visible()
    booking_ref = event_page.booking_ref()
    cleanup_ui_bookings.append(booking_ref)

    event_page.nav_my_bookings.click()

    card = MyBookingsPage(logged_in_page).card_for(booking_ref)
    expect(card).to_be_visible()
    expect(card).to_contain_text(test_event["title"])
    expect(card).to_contain_text(f"{quantity} tickets")
    expect(card).to_contain_text("confirmed")



# U3 | AC4 | Cancel a booking from My Bookings → it disappears (booking created via API)
def test_user_can_cancel_booking_from_my_bookings(
    logged_in_page, test_event, create_booking, bookings_api
):
    response = create_booking(booking_payload(test_event["id"], quantity=1))
    assert response.status == 201, response.text()
    booking = response.json()["data"]

    my_bookings = MyBookingsPage(logged_in_page).open()
    expect(my_bookings.card_for(booking["bookingRef"])).to_be_visible()

    my_bookings.cancel(booking["bookingRef"])

    expect(my_bookings.card_for(booking["bookingRef"])).to_have_count(0)
    assert bookings_api.get(booking["id"]).status == 404