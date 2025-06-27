"""Content validation utilities."""

from typing import Any, ClassVar
from urllib.parse import urlparse

from content.html import HTMLProcessor


class ContentValidator:
    """Content validation for Telegraph compatibility."""

    MAX_TITLE_LENGTH: ClassVar[int] = 256
    MAX_CONTENT_SIZE: ClassVar[int] = 64 * 1024
    ALLOWED_SCHEMES: ClassVar[set[str]] = {"http", "https"}

    def __init__(self) -> None:
        """Initialize content validator."""
        self._html_processor = HTMLProcessor()

    def validate_title(self, title: str) -> bool:
        """Validate page title.

        Args:
        ----
            title: Page title

        Returns:
        -------
            True if title is valid

        """
        return 1 <= len(title) <= self.MAX_TITLE_LENGTH

    def validate_content_size(self, content: str) -> bool:
        """Validate content size.

        Args:
        ----
            content: Content string

        Returns:
        -------
            True if content size is valid

        """
        return len(content.encode("utf-8")) <= self.MAX_CONTENT_SIZE

    def validate_url(self, url: str) -> bool:
        """Validate URL format.

        Args:
        ----
            url: URL to validate

        Returns:
        -------
            True if URL is valid

        """
        try:
            result = urlparse(url)
            return all([result.scheme in self.ALLOWED_SCHEMES, result.netloc])
        except ValueError:
            return False

    def sanitize_html(self, html: str) -> str:
        """Sanitize HTML content.

        Args:
        ----
            html: Raw HTML

        Returns:
        -------
            Sanitized HTML

        """
        return self._html_processor.sanitize_html(html)

    def html_to_nodes(self, html: str) -> list[dict[str, Any]]:
        """Convert HTML to Telegraph nodes with validation.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            Validated Telegraph nodes

        """
        nodes = self._html_processor.html_to_nodes(html)
        if not self.validate_nodes(nodes):
            raise ValueError("Invalid node structure")
        return nodes

    def validate_nodes(self, nodes: list[dict[str, Any]]) -> bool:
        """Validate Telegraph node structure.

        Args:
        ----
            nodes: Telegraph nodes

        Returns:
        -------
            True if nodes are valid

        """
        return all(self._validate_single_node(node) for node in nodes)

    def _validate_single_node(self, node: dict[str, Any]) -> bool:
        """Validate single Telegraph node.

        Args:
        ----
            node: Telegraph node

        Returns:
        -------
            True if node is valid

        """
        if isinstance(node, str):
            return True

        if "tag" not in node:
            return False

        if "children" in node:
            return self.validate_nodes(node["children"])

        return True
