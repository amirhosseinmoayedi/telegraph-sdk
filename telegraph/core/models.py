"""Telegraph data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Union, ClassVar


@dataclass(frozen=True)
class TelegraphAccount:
    """Telegraph account information."""

    short_name: str
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    access_token: Optional[str] = None
    auth_url: Optional[str] = None
    page_count: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert account to dictionary.

        Returns
        -------
            Dictionary representation of account

        """
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass(frozen=True)
class PageContent:
    """Telegraph page content representation."""

    title: str
    content: Union[str, list[dict[str, Any]]]
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    content_type: str = "html"
    MAX_TITLE_LENGTH: ClassVar[int] = 256

    def __post_init__(self) -> None:
        """Validate page content after initialization."""
        if not (1 <= len(self.title) <= self.MAX_TITLE_LENGTH):
            raise ValueError("Title must be 1-256 characters long")

        if self.content_type not in ["html", "markdown", "nodes"]:
            raise ValueError("Content type must be 'html', 'markdown', or 'nodes'")


@dataclass(frozen=True)
class TelegraphPage:
    """Telegraph page information."""

    path: str
    url: str
    title: str
    description: Optional[str] = None
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    image_url: Optional[str] = None
    content: Optional[list[dict[str, Any]]] = None
    views: Optional[int] = None
    can_edit: bool = False
    created_at: Optional[datetime] = None

    @property
    def full_url(self) -> str:
        """Get full Telegraph URL.

        Returns
        -------
            Complete Telegraph URL

        """
        return f"https://telegra.ph/{self.path}"

    def to_dict(self) -> dict[str, Any]:
        """Convert page to dictionary.

        Returns
        -------
            Dictionary representation of page

        """
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        return data


@dataclass(frozen=True)
class UploadResult:
    """File upload result."""

    success: bool
    url: Optional[str] = None
    error: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    upload_time: Optional[datetime] = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert upload result to dictionary.

        Returns
        -------
            Dictionary representation of upload result

        """
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        if self.upload_time:
            data["upload_time"] = self.upload_time.isoformat()
        return data


@dataclass(frozen=True)
class ViewStats:
    """Page view statistics."""

    views: int
    period: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert view stats to dictionary.

        Returns
        -------
            Dictionary representation of view stats

        """
        return {k: v for k, v in self.__dict__.items() if v is not None}
