from playwright.sync_api import Page

from config.settings import settings


class BasePage:
    """Shared parts of every EventHub page: navigation bar and URL handling."""

    def __init__(self, page: Page):
        self.page = page
        self.nav_events = page.get_by_test_id("nav-events")
        self.nav_my_bookings = page.get_by_test_id("nav-bookings")
        self.user_email = page.get_by_test_id("user-email-display")

    def goto(self, path: str):
        self.page.goto(settings.ui_base_url.rstrip("/") + path)
        return self