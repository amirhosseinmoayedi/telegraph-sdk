"""Main Telegraph client implementation."""

import asyncio
import json
from typing import Any, Optional

import aiohttp

from telegraph.analytics import Analytics
from telegraph.content import ContentValidator, MarkdownProcessor
from telegraph.core import (
    PageContent,
    TelegraphAccount,
    TelegraphAPIError,
    TelegraphError,
    TelegraphPage,
    ValidationError,
    ViewStats,
)
from telegraph.upload import FileUploader

HTTP_OK = 200
SHORT_NAME_MAX_LENGTH = 32

class TelegraphClient:
    """Async Telegraph API client with comprehensive functionality."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        domain: str = "telegra.ph",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        """Initialize Telegraph client.

        Args:
        ----
            access_token: Telegraph access token
            domain: Telegraph domain
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts

        """
        self._access_token = access_token
        self._domain = domain
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._max_retries = max_retries

        self._markdown_processor = MarkdownProcessor()
        self._content_validator = ContentValidator()
        self._file_uploader = FileUploader(domain=domain, timeout=timeout)
        self._analytics = Analytics(self)

    @property
    def access_token(self) -> Optional[str]:
        """Get current access token.

        Returns
        -------
            Current access token

        """
        return self._access_token

    @property
    def domain(self) -> str:
        """Get Telegraph domain.

        Returns
        -------
            Telegraph domain

        """
        return self._domain

    @property
    def markdown(self) -> MarkdownProcessor:
        """Get markdown processor.

        Returns
        -------
            Markdown processor instance

        """
        return self._markdown_processor

    @property
    def uploader(self) -> FileUploader:
        """Get file uploader.

        Returns
        -------
            File uploader instance

        """
        return self._file_uploader

    @property
    def analytics(self) -> Analytics:
        """Get analytics interface.

        Returns
        -------
            Analytics instance

        """
        return self._analytics

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make HTTP request to Telegraph API.

        Args:
        ----
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            files: Files to upload

        Returns:
        -------
            API response data

        Raises:
        ------
            TelegraphAPIError: API request failed

        """
        url = f"https://api.{self._domain}/{endpoint}"

        if data is None:
            data = {}

        if self._access_token and "access_token" not in data:
            data["access_token"] = self._access_token

        for attempt in range(self._max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=self._timeout) as session:
                    if method.upper() == "POST":
                        if files:
                            form_data = aiohttp.FormData()
                            for key, value in data.items():
                                form_data.add_field(key, str(value))
                            for key, file_data in files.items():
                                form_data.add_field(key, file_data)
                            async with session.post(url, data=form_data) as response:
                                result = await response.json()
                        else:
                            async with session.post(url, data=data) as response:
                                result = await response.json()
                    else:
                        async with session.get(url, params=data) as response:
                            result = await response.json()

                if result.get("ok"):
                    return result["result"]
                else:
                    error = result.get("error", "Unknown error")
                    if "FLOOD_WAIT" in str(error) and attempt < self._max_retries:
                        wait_time = int(str(error).split("_")[-1])
                        await asyncio.sleep(wait_time)
                        continue
                    raise TelegraphAPIError(f"API Error: {error}", response_data=result)

            except aiohttp.ClientError as e:
                if attempt == self._max_retries:
                    raise TelegraphAPIError(
                        f"Request failed after {self._max_retries} retries: {e}"
                    ) from e
                await asyncio.sleep(2**attempt)

        raise TelegraphAPIError("Max retries exceeded")

    async def create_account(
        self,
        short_name: str,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
        replace_token: bool = True,
    ) -> TelegraphAccount:
        """Create new Telegraph account.

        Args:
        ----
            short_name: Account name (1-32 characters)
            author_name: Default author name
            author_url: Default profile link
            replace_token: Replace current access token

        Returns:
        -------
            Created Telegraph account

        Raises:
        ------
            ValidationError: Invalid input parameters
            TelegraphAPIError: Account creation failed

        """
        if not (1 <= len(short_name) <= SHORT_NAME_MAX_LENGTH):
            raise ValidationError(
                "short_name", f"must be 1-{SHORT_NAME_MAX_LENGTH} characters long", short_name
            )

        data = {"short_name": short_name}
        if author_name:
            data["author_name"] = author_name
        if author_url:
            data["author_url"] = author_url

        result = await self._make_request("POST", "createAccount", data)

        account = TelegraphAccount(
            short_name=result["short_name"],
            author_name=result.get("author_name"),
            author_url=result.get("author_url"),
            access_token=result.get("access_token"),
            auth_url=result.get("auth_url"),
        )

        if replace_token and account.access_token:
            self._access_token = account.access_token

        return account

    async def get_account_info(self, fields: Optional[list[str]] = None) -> TelegraphAccount:
        """Get account information.

        Args:
        ----
            fields: Fields to retrieve

        Returns:
        -------
            Account information

        Raises:
        ------
            TelegraphError: No access token
            TelegraphAPIError: Request failed

        """
        if not self._access_token:
            raise TelegraphError("Access token required")

        if fields is None:
            fields = ["short_name", "author_name", "author_url", "page_count"]

        data = {"fields": json.dumps(fields)}
        result = await self._make_request("POST", "getAccountInfo", data)

        return TelegraphAccount(
            short_name=result["short_name"],
            author_name=result.get("author_name"),
            author_url=result.get("author_url"),
            page_count=result.get("page_count"),
        )

    async def edit_account_info(
        self,
        short_name: Optional[str] = None,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
    ) -> TelegraphAccount:
        """Edit account information.

        Args:
        ----
            short_name: New account name
            author_name: New author name
            author_url: New author URL

        Returns:
        -------
            Updated account information

        Raises:
        ------
            TelegraphError: No access token or no fields provided
            TelegraphAPIError: Request failed

        """
        if not self._access_token:
            raise TelegraphError("Access token required")

        data = {}
        if short_name:
            data["short_name"] = short_name
        if author_name:
            data["author_name"] = author_name
        if author_url:
            data["author_url"] = author_url

        if not data:
            raise ValidationError("fields", "At least one field must be provided")

        result = await self._make_request("POST", "editAccountInfo", data)

        return TelegraphAccount(
            short_name=result["short_name"],
            author_name=result.get("author_name"),
            author_url=result.get("author_url"),
        )

    async def create_page(self, content: PageContent) -> TelegraphPage:
        """Create new Telegraph page.

        Args:
        ----
            content: Page content configuration

        Returns:
        -------
            Created Telegraph page

        Raises:
        ------
            TelegraphAPIError: Page creation failed

        """
        processed_content = await self._process_content(content)

        data = {
            "title": content.title,
            "content": json.dumps(processed_content),
            "return_content": False,
        }

        if content.author_name:
            data["author_name"] = content.author_name
        if content.author_url:
            data["author_url"] = content.author_url

        result = await self._make_request("POST", "createPage", data)

        return TelegraphPage(
            path=result["path"],
            url=result["url"],
            title=result["title"],
            author_name=result.get("author_name"),
            author_url=result.get("author_url"),
            can_edit=result.get("can_edit", False),
        )

    async def edit_page(self, path: str, content: PageContent) -> TelegraphPage:
        """Edit existing Telegraph page.

        Args:
        ----
            path: Page path
            content: New page content

        Returns:
        -------
            Updated Telegraph page

        Raises:
        ------
            TelegraphError: No access token
            TelegraphAPIError: Edit failed

        """
        if not self._access_token:
            raise TelegraphError("Access token required")

        processed_content = await self._process_content(content)

        data = {
            "path": path,
            "title": content.title,
            "content": json.dumps(processed_content),
            "return_content": False,
        }

        if content.author_name:
            data["author_name"] = content.author_name
        if content.author_url:
            data["author_url"] = content.author_url

        result = await self._make_request("POST", "editPage", data)

        return TelegraphPage(
            path=result["path"],
            url=result["url"],
            title=result["title"],
            author_name=result.get("author_name"),
            author_url=result.get("author_url"),
            can_edit=result.get("can_edit", False),
        )

    async def get_page(self, path: str, return_content: bool = True) -> TelegraphPage:
        """Get Telegraph page information.

        Args:
        ----
            path: Page path
            return_content: Include page content

        Returns:
        -------
            Telegraph page information

        Raises:
        ------
            TelegraphAPIError: Request failed

        """
        data = {"path": path, "return_content": return_content}

        result = await self._make_request("GET", "getPage", data)

        return TelegraphPage(
            path=result["path"],
            url=result["url"],
            title=result["title"],
            description=result.get("description"),
            author_name=result.get("author_name"),
            author_url=result.get("author_url"),
            image_url=result.get("image_url"),
            content=result.get("content") if return_content else None,
            views=result.get("views"),
            can_edit=result.get("can_edit", False),
        )

    async def get_page_list(self, offset: int = 0, limit: int = 50) -> list[TelegraphPage]:
        """Get list of account pages.

        Args:
        ----
            offset: Pagination offset
            limit: Number of pages to retrieve

        Returns:
        -------
            List of Telegraph pages

        Raises:
        ------
            TelegraphError: No access token
            TelegraphAPIError: Request failed

        """
        if not self._access_token:
            raise TelegraphError("Access token required")

        data = {"offset": offset, "limit": min(limit, 200)}

        result = await self._make_request("POST", "getPageList", data)

        pages = []
        for page_data in result["pages"]:
            pages.append(
                TelegraphPage(
                    path=page_data["path"],
                    url=page_data["url"],
                    title=page_data["title"],
                    description=page_data.get("description"),
                    author_name=page_data.get("author_name"),
                    author_url=page_data.get("author_url"),
                    image_url=page_data.get("image_url"),
                    views=page_data["views"],
                    can_edit=page_data.get("can_edit", False),
                )
            )

        return pages

    async def get_views(self, path: str, **kwargs) -> ViewStats:
        """Get page views.

        Args:
        ----
            path: Page path
            **kwargs: year, month, day, hour

        Returns:
        -------
            Page view statistics

        """
        return await self._analytics.get_views(path, **kwargs)

    async def revoke_access_token(self) -> TelegraphAccount:
        """Revoke current access token.

        Returns
        -------
            Account with new access token

        Raises
        ------
            TelegraphError: No access token
            TelegraphAPIError: Request failed

        """
        if not self._access_token:
            raise TelegraphError("Access token required")

        result = await self._make_request("POST", "revokeAccessToken")

        account = TelegraphAccount(
            short_name=result["short_name"],
            author_name=result.get("author_name"),
            author_url=result.get("author_url"),
            access_token=result.get("access_token"),
            auth_url=result.get("auth_url"),
        )

        self._access_token = account.access_token
        return account

    async def _process_content(self, content: PageContent) -> list[dict[str, Any]]:
        """Process content based on its type.

        Args:
        ----
            content: Page content object

        Returns:
        -------
            Processed content as Telegraph nodes

        """
        if content.content_type == "markdown":
            html = self._markdown_processor.convert(content.content)
            return self._content_validator.html_to_nodes(html)

        elif content.content_type == "html":
            return self._content_validator.html_to_nodes(content.content)

        elif content.content_type == "nodes":
            if self._content_validator.validate_nodes(content.content):
                return content.content
            else:
                raise ValidationError("content", "Invalid node structure")

        else:
            raise ValueError(f"Unsupported content type: {content.content_type}")
