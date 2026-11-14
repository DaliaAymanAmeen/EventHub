import pytest

from api_clients.auth_api import AuthApi
from api_clients.bookings_api import BookingsApi
from config.settings import settings
from data.factories import booking_payload

pytestmark = pytest.mark.api

# A10 | AC5 | POST /bookings without a token returns 401
def test_create_booking_without_token_is_rejected(anonymous_request, test_event):
    response = BookingsApi(anonymous_request).create(booking_payload(test_event["id"]))

    assert response.status == 401, response.text()


# A10 | — | An invalid token is rejected with 401
def test_request_with_invalid_token_is_rejected(invalid_token_request):
    response = AuthApi(invalid_token_request).me()

    assert response.status == 401, response.text()


# A14 | — | Framework check: session token belongs to the configured account
def test_framework_token_belongs_to_configured_user(api_request):
    response = AuthApi(api_request).me()

    assert response.status == 200, response.text()
    assert response.json()["user"]["email"] == settings.email