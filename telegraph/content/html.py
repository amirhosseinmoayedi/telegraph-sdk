"""HTML processing utilities."""

from html.parser import HTMLParser
from typing import Any, ClassVar

from bs4 import BeautifulSoup


class TelegraphHTMLParser(HTMLParser):
    """HTML parser optimized for Telegraph content."""

    ALLOWED_TAGS: ClassVar[set[str]] = {
        "a",
        "aside",
        "b",
        "blockquote",
        "br",
        "code",
        "em",
        "figcaption",
        "figure",
        "h3",
        "h4",
        "hr",
        "i",
        "iframe",
        "img",
        "li",
        "ol",
        "p",
        "pre",
        "s",
        "strong",
        "u",
        "ul",
        "video",
    }
    ALLOWED_ATTRIBUTES: ClassVar[dict[str, set[str]]] = {
        "a": {"href", "title"},
        "img": {"src", "alt", "title"},
        "iframe": {"src", "width", "height"},
        "video": {"src", "width", "height", "controls"},
    }

    def __init__(self) -> None:
        """Initialize Telegraph HTML parser."""
        super().__init__()
        self.nodes: list[dict[str, Any]] = []
        self.current_nodes: list[dict[str, Any]] = self.nodes
        self.parent_stack: list[list[dict[str, Any]]] = []
        self.tag_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        """Handle opening HTML tag.

        Args:
        ----
            tag: HTML tag name
            attrs: Tag attributes

        """
        if tag in self.ALLOWED_TAGS:
            node = {"tag": tag, "attrs": {}, "children": []}
            for attr, value in attrs:
                if attr in self.ALLOWED_ATTRIBUTES.get(tag, set()):
                    node["attrs"][attr] = value

            self.current_nodes.append(node)
            self.parent_stack.append(self.current_nodes)
            self.current_nodes = node["children"]
            self.tag_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        """Handle closing HTML tag.

        Args:
        ----
            tag: HTML tag name

        """
        if self.tag_stack and tag == self.tag_stack[-1]:
            self.tag_stack.pop()
            self.current_nodes = self.parent_stack.pop()

    def handle_data(self, data: str) -> None:
        """Handle text data.

        Args:
        ----
            data: Text content

        """
        if data.strip():
            self.current_nodes.append(data)

    def get_nodes(self) -> list[dict[str, Any]]:
        """Get parsed Telegraph nodes.

        Returns
        -------
            List of Telegraph-compatible nodes

        """
        return self.nodes


class HTMLProcessor:
    """HTML processing utilities for Telegraph."""

    def __init__(self) -> None:
        """Initialize HTML processor."""
        self._parser = TelegraphHTMLParser()

    def sanitize_html(self, html: str) -> str:
        """Sanitize HTML for Telegraph compatibility.

        Args:
        ----
            html: Raw HTML content

        Returns:
        -------
            Sanitized HTML content

        """
        html = self._remove_scripts_and_styles(html)
        html = self._normalize_whitespace(html)
        html = self._fix_malformed_tags(html)
        nodes = self.html_to_nodes(html)
        return self.nodes_to_html(nodes)

    def html_to_nodes(self, html: str) -> list[dict[str, Any]]:
        """Convert HTML to Telegraph nodes.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            Telegraph node structure

        """
        self._parser.feed(html)
        nodes = self._parser.get_nodes()
        self._parser.reset()
        return nodes

    def nodes_to_html(self, nodes: list[dict[str, Any]]) -> str:
        """Convert Telegraph nodes back to HTML.

        Args:
        ----
            nodes: Telegraph node structure

        Returns:
        -------
            HTML content

        """
        html = ""
        for node in nodes:
            html += self._node_to_html(node)
        return html

    def _node_to_html(self, node: dict[str, Any]) -> str:
        """Convert single node to HTML.

        Args:
        ----
            node: Telegraph node

        Returns:
        -------
            HTML representation

        """
        if isinstance(node, str):
            return node

        tag = node.get("tag", "")
        attrs = " ".join([f'{k}="{v}"' for k, v in node.get("attrs", {}).items()])
        children = self.nodes_to_html(node.get("children", []))

        return f"<{tag} {attrs}>{children}</{tag}>"

    def _remove_scripts_and_styles(self, html: str) -> str:
        """Remove script and style tags.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            Cleaned HTML

        """
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return str(soup)

    def _normalize_whitespace(self, html: str) -> str:
        """Normalize whitespace in HTML.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            Normalized HTML

        """
        return " ".join(html.split())

    def _fix_malformed_tags(self, html: str) -> str:
        """Fix common malformed HTML patterns.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            Fixed HTML

        """
        soup = BeautifulSoup(html, "html.parser")
        return str(soup)
