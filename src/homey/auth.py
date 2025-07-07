"""Authentication handler for the Homey API."""

from typing import Optional

import httpx

from .exceptions import HomeyAuthenticationError, HomeyConnectionError


class HomeyAuth:
    """Handle authentication for the Homey API."""

    def __init__(self, base_url: str, token: str) -> None:
        """Initialize the authentication handler."""
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._authenticated = False
        self._session_info: Optional[dict] = None

    async def authenticate(self) -> bool:
        """Authenticate with the Homey API."""
        if not self.token:
            raise HomeyAuthenticationError("No token provided")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test authentication by making a request to the system endpoint
                response = await client.get(
                    f"{self.base_url}/api/manager/system",
                    headers={"Authorization": f"Bearer {self.token}"},
                )

                if response.status_code == 200:
                    self._authenticated = True
                    self._session_info = response.json()
                    return True
                elif response.status_code == 401:
                    raise HomeyAuthenticationError("Invalid token")
                elif response.status_code == 403:
                    raise HomeyAuthenticationError("Insufficient permissions")
                else:
                    raise HomeyAuthenticationError(
                        f"Authentication failed with status {response.status_code}"
                    )

        except httpx.TimeoutException:
            raise HomeyConnectionError("Authentication request timed out")
        except httpx.ConnectError:
            raise HomeyConnectionError("Failed to connect to Homey")
        except httpx.RequestError as e:
            raise HomeyConnectionError(f"Authentication request failed: {str(e)}")

    async def validate_token(self) -> bool:
        """Validate the current token."""
        try:
            return await self.authenticate()
        except HomeyAuthenticationError:
            return False

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._authenticated

    def get_session_info(self) -> Optional[dict]:
        """Get session information."""
        return self._session_info

    def get_headers(self) -> dict:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def create_personal_access_token_url(homey_url: str) -> str:
        """Create a URL for generating a Personal Access Token."""
        base_url = homey_url.rstrip("/")
        return f"{base_url}/manager/users/token"

    @staticmethod
    def validate_token_format(token) -> bool:
        """Validate token format (basic check)."""
        if not token:
            return False

        # Basic validation - tokens should be non-empty strings
        # More specific validation could be added based on Homey's token format
        return isinstance(token, str) and len(token.strip()) > 0

    @staticmethod
    def validate_url_format(url) -> bool:
        """Validate Homey URL format."""
        if not url:
            return False

        if not isinstance(url, str):
            return False

        url = url.strip()
        return (url.startswith("http://") or url.startswith("https://")) and len(
            url
        ) > 10
