from playwright.sync_api import APIRequestContext, APIResponse


class BookingsApi:
    """Client for the /bookings endpoints."""

    def __init__(self, request: APIRequestContext):
        self._request = request

    def create(self, payload: dict) -> APIResponse:
        return self._request.post("bookings", data=payload)

    def get(self, booking_id: int) -> APIResponse:
        return self._request.get(f"bookings/{booking_id}")

    def get_by_ref(self, booking_ref: str) -> APIResponse:
        return self._request.get(f"bookings/ref/{booking_ref}")

    def list(self, **filters) -> APIResponse:
        return self._request.get("bookings", params=filters)

    def cancel(self, booking_id: int) -> APIResponse:
        return self._request.delete(f"bookings/{booking_id}")