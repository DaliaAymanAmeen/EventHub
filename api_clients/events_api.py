from playwright.sync_api import APIRequestContext, APIResponse


class EventsApi:
    """Client for the /events endpoints (used for test-data setup)."""

    def __init__(self, request: APIRequestContext):
        self._request = request

    def create(self, payload: dict) -> APIResponse:
        return self._request.post("events", data=payload)

    def get(self, event_id: int) -> APIResponse:
        return self._request.get(f"events/{event_id}")

    def delete(self, event_id: int) -> APIResponse:
        return self._request.delete(f"events/{event_id}")