from pages.base_page import BasePage


class MyBookingsPage(BasePage):
    """My Bookings page at /bookings: booking cards and the cancel flow."""

    def __init__(self, page):
        super().__init__(page)
        self.booking_cards = page.get_by_test_id("booking-card")
        self.confirm_cancel_button = page.get_by_test_id("confirm-dialog-yes")

    def open(self):
        self.goto("/bookings")
        return self

    def card_for(self, booking_ref: str):
        """The booking card that shows this booking reference."""
        return self.booking_cards.filter(has_text=booking_ref)

    def cancel(self, booking_ref: str):
        """Click Cancel on the booking's card, then confirm in the dialog."""
        self.card_for(booking_ref).get_by_test_id("cancel-booking-btn").click()
        self.confirm_cancel_button.click()
        return self