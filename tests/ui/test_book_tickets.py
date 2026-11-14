from decimal import Decimal

import pytest
from playwright.sync_api import expect

from data.factories import new_customer
from pages.event_details_page import EventDetailsPage

pytestmark = pytest.mark.ui


# U1 | AC1, AC2 | Book tickets → confirmation shows ref, customer, tickets; backend total correct
@pytest.mark.smoke
def test_user_can_book_tickets_and_sees_confirmation(
    logged_in_page, test_event, bookings_api, cleanup_ui_bookings
):
    customer = new_customer()
    quantity = 3

    event_page = EventDetailsPage(logged_in_page).open(test_event["id"])
    event_page.book(customer, quantity=quantity)

    expect(event_page.confirmation_heading).to_be_visible()
    booking_ref = event_page.booking_ref()
    cleanup_ui_bookings.append(booking_ref)

    expect(event_page.confirmation_value("Customer")).to_have_text(customer["customerName"])
    expect(event_page.confirmation_value("Tickets")).to_have_text(str(quantity))

    # The booking shown in the UI really exists in the backend, with the right total
    saved = bookings_api.get_by_ref(booking_ref)
    assert saved.status == 200, saved.text()
    booking = saved.json()["data"]
    assert booking["quantity"] == quantity
    assert Decimal(str(booking["totalPrice"])) == Decimal(str(test_event["price"])) * quantity



# U5 | AC2 | Total shown on the confirmation = price × quantity (whole and decimal prices)
@pytest.mark.parametrize(
    "price",
    [
        pytest.param(250, id="whole-price"),
        pytest.param(
            99.99,
            id="decimal-price",
            marks=pytest.mark.xfail(
                reason="BUG: UI rounds prices to whole dollars "
                       "($99.99 shown as $100; 3 tickets shown as $300, backend stores 299.97)",
                strict=True,
            ),
        ),
    ],
)
def test_confirmation_total_is_price_times_quantity(
    logged_in_page, create_event, cleanup_ui_bookings, price
):
    event = create_event(price=price)
    quantity = 3

    event_page = EventDetailsPage(logged_in_page).open(event["id"])
    event_page.book(new_customer(), quantity=quantity)

    expect(event_page.confirmation_heading).to_be_visible()
    cleanup_ui_bookings.append(event_page.booking_ref())

    assert event_page.total() == Decimal(str(price)) * quantity