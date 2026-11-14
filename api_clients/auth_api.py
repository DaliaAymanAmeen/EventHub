from playwright.sync_api import APIRequestContext, APIResponse


class AuthApi:
    """Client for the /auth endpoints."""

    def __init__(self, request: APIRequestContext):
        self._request = request

    def login(self, email: str, password: str) -> APIResponse:
        return self._request.post(
            "auth/login",
            data={"email": email, "password": password},
        )

    def me(self) -> APIResponse:
        return self._request.get("auth/me")