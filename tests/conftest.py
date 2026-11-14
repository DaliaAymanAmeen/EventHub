"""Shared fixtures: authentication, API clients, test data and cleanup.

Tests never log in, build URLs or clean up themselves. They ask for a
fixture by name and pytest provides it.
"""
import pytest
from playwright.sync_api import APIRequestContext, Playwright

from api_clients.auth_api import AuthApi
from api_clients.bookings_api import BookingsApi
from api_clients.events_api import EventsApi
from config.settings import settings
from data.factories import booking_payload, event_payload

# Playwright joins URLs like a browser, so the base must end with "/"
API_BASE_URL = settings.api_base_url.rstrip("/") + "/"


# ---------- Authentication ----------

@pytest.fixture(scope="session")
def auth_token(playwright: Playwright) -> str:
    """Log in once per test run and return the JWT."""
    request = playwright.request.new_context(base_url=API_BASE_URL)
    try:
        response = AuthApi(request).login(settings.email, settings.password)
        if not response.ok:
            raise RuntimeError(
                f"Login failed for {settings.email}: "
                f"{response.status} {response.text()}"
            )
        return response.json()["token"]
    finally:
        request.dispose()


@pytest.fixture(scope="session")
def api_request(playwright: Playwright, auth_token: str) -> APIRequestContext:
    """Request context that sends the token on every call."""
    request = playwright.request.new_context(
        base_url=API_BASE_URL,
        extra_http_headers={"Authorization": f"Bearer {auth_token}"},
    )
    yield request
    request.dispose()


# ---------- API clients ----------

@pytest.fixture(scope="session")
def events_api(api_request: APIRequestContext) -> EventsApi:
    return EventsApi(api_request)


@pytest.fixture(scope="session")
def bookings_api(api_request: APIRequestContext) -> BookingsApi:
    return BookingsApi(api_request)


# ---------- Test data ----------

@pytest.fixture(scope="session")
def test_event(events_api: EventsApi) -> dict:
    """One event owned by the test run, with a known price and seat count.

    Deleted at the end of the run; deleting an event also deletes its bookings.
    """
    response = events_api.create(event_payload())
    assert response.status == 201, f"Could not create test event: {response.text()}"
    event = response.json()["data"]
    yield event
    events_api.delete(event["id"])


@pytest.fixture
def create_booking(bookings_api: BookingsApi):
    """Create bookings through this fixture and they're cancelled after the test.

    Usage in a test:  response = create_booking(payload)
    """
    created_ids = []

    def _create(payload: dict):
        response = bookings_api.create(payload)
        if response.status == 201:
            created_ids.append(response.json()["data"]["id"])
        return response

    yield _create

    for booking_id in created_ids:
        bookings_api.cancel(booking_id)  # a 404 is fine: the test may have cancelled it



# ---------- Unauthenticated clients (for negative auth tests) ----------

@pytest.fixture(scope="session")
def anonymous_request(playwright: Playwright) -> APIRequestContext:
    """Request context with NO token."""
    request = playwright.request.new_context(base_url=API_BASE_URL)
    yield request
    request.dispose()


@pytest.fixture(scope="session")
def invalid_token_request(playwright: Playwright) -> APIRequestContext:
    """Request context with a token the server will reject."""
    request = playwright.request.new_context(
        base_url=API_BASE_URL,
        extra_http_headers={"Authorization": "Bearer invalid.token.value"},
    )
    yield request
    request.dispose()


# ---------- More test data ----------

@pytest.fixture
def create_event(events_api: EventsApi):
    """Create extra events with custom fields; deleted after the test.

    Usage:  event = create_event(totalSeats=2)
    """
    created_ids = []

    def _create(**overrides) -> dict:
        response = events_api.create(event_payload(**overrides))
        assert response.status == 201, f"Could not create event: {response.text()}"
        event = response.json()["data"]
        created_ids.append(event["id"])
        return event

    yield _create

    for event_id in created_ids:
        events_api.delete(event_id)


@pytest.fixture
def booking(test_event: dict, create_booking) -> dict:
    """A ready-made confirmed booking, for tests that need one to exist first."""
    response = create_booking(booking_payload(test_event["id"], quantity=2))
    assert response.status == 201, f"Could not create booking: {response.text()}"
    return response.json()["data"]