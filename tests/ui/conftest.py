"""UI-only fixtures. Shared fixtures (auth_token, test_event, ...) come from tests/conftest.py."""
import json

import pytest
from playwright.sync_api import Page, expect

from api_clients.bookings_api import BookingsApi
from config.settings import settings

TOKEN_STORAGE_KEY = "eventhub_token"

# The app's lists load slowly; give web-first assertions more time than the 5 s default
expect.set_options(timeout=10_000)


@pytest.fixture
def logged_in_page(page: Page, auth_token: str) -> Page:
    """A browser page that is already logged in, without using the login form.

    The app keeps its JWT in localStorage['eventhub_token']. An init script puts
    our token there before the app's own code runs on every page load.
    """
    origin = settings.ui_base_url.rstrip("/")
    page.add_init_script(
        f"""
        if (window.location.origin === {json.dumps(origin)}) {{
            window.localStorage.setItem({json.dumps(TOKEN_STORAGE_KEY)}, {json.dumps(auth_token)});
        }}
        """
    )
    return page


@pytest.fixture
def cleanup_ui_bookings(bookings_api: BookingsApi):
    """Collect booking refs created through the UI; they're cancelled via the API afterwards.

    Usage in a test:  cleanup_ui_bookings.append(booking_ref)
    """
    refs = []
    yield refs
    for ref in refs:
        response = bookings_api.get_by_ref(ref)
        if response.ok:
            bookings_api.cancel(response.json()["data"]["id"])