from decimal import Decimal

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class EventDetailsPage(BasePage):
    """Event page at /events/{id}: booking form and booking confirmation."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Booking form
        self.increase_tickets = page.get_by_role("button", name="+", exact=True)
        self.ticket_count = page.locator("#ticket-count")
        self.full_name = page.get_by_label("Full Name")
        self.email = page.get_by_label("Email")
        self.phone = page.get_by_label("Phone Number")
        self.confirm_button = page.get_by_role("button", name="Confirm Booking")
        # Confirmation (shown after a successful booking)
        self.confirmation_heading = page.get_by_role("heading", name="Booking Confirmed")

    def open(self, event_id: int):
        self.goto(f"/events/{event_id}")
        expect(self.confirm_button).to_be_visible()
        return self

    def set_quantity(self, quantity: int):
        """Quantity starts at 1; click + until it reaches the wanted number."""
        for _ in range(quantity - 1):
            self.increase_tickets.click()
        expect(self.ticket_count).to_have_text(str(quantity))
        return self

    def fill_customer(self, customer: dict):
        self.full_name.fill(customer["customerName"])
        self.email.fill(customer["customerEmail"])
        self.phone.fill(customer["customerPhone"])
        return self

    def confirm(self):
        self.confirm_button.click()
        return self

    def book(self, customer: dict, quantity: int = 1):
        """Full user action: choose tickets, fill details, confirm."""
        return self.set_quantity(quantity).fill_customer(customer).confirm()

    # ----- Confirmation details -----

    def confirmation_value(self, label: str):
        """The value shown next to a label in the confirmation, e.g. 'Booking Ref'."""
        return self.page.get_by_text(label, exact=True).locator("xpath=following-sibling::*[1]")

    def booking_ref(self) -> str:
        return self.confirmation_value("Booking Ref").inner_text().strip()

    def total(self) -> Decimal:
        """Total shown in the confirmation, e.g. '$1,299.87' → Decimal('1299.87')."""
        text = self.confirmation_value("Total").inner_text()
        return Decimal(text.replace("$", "").replace(",", "").strip())

    def validation_error(self, message: str):
        """A validation message shown under a form field, e.g. 'Enter a valid email'."""
        return self.page.locator("form").get_by_text(message)