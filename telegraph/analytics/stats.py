"""Analytics interface for Telegraph."""

from typing import TYPE_CHECKING, Any, Optional

from telegraph.core.models import ViewStats

if TYPE_CHECKING:
    from telegraph.core.client import TelegraphClient


class Analytics:
    """Interface for Telegraph analytics."""

    def __init__(self, client: "TelegraphClient") -> None:
        """Initialize analytics interface.

        Args:
        ----
            client: Telegraph client instance

        """
        self._client = client

    async def get_views(
        self,
        path: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
    ) -> ViewStats:
        """Get page views by date.

        Args:
        ----
            path: Page path
            year: Year (2000-2100)
            month: Month (1-12)
            day: Day (1-31)
            hour: Hour (0-24)

        Returns:
        -------
            View statistics

        """
        params: dict[str, Any] = {"path": path}
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        if day:
            params["day"] = day
        if hour:
            params["hour"] = hour

        response = await self._client._make_request("GET", "getViews", params)
        return ViewStats(**response)
