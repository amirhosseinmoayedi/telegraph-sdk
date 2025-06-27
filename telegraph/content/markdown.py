"""Advanced markdown processor for Telegraph."""

import re
from typing import Any, Optional

import markdown
from bs4 import BeautifulSoup

TELEGRAPH_EXTENSIONS: list[str] = [
    "markdown.extensions.extra",
    "markdown.extensions.codehilite",
    "markdown.extensions.tables",
    "markdown.extensions.toc",
]


class MarkdownProcessor:
    """Advanced markdown processor optimized for Telegraph."""

    def __init__(self, custom_extensions: Optional[list[str]] = None) -> None:
        """Initialize markdown processor.

        Args:
        ----
            custom_extensions: Additional markdown extensions

        """
        extensions = TELEGRAPH_EXTENSIONS.copy()
        if custom_extensions:
            extensions.extend(custom_extensions)

        self._processor = markdown.Markdown(
            extensions=extensions,
            extension_configs={
                "markdown.extensions.codehilite": {
                    "css_class": "highlight",
                    "use_pygments": False,
                },
                "markdown.extensions.toc": {
                    "permalink": False,
                },
            },
        )

    def convert(self, markdown_text: str) -> str:
        """Convert markdown to Telegraph-compatible HTML.

        Args:
        ----
            markdown_text: Markdown content

        Returns:
        -------
            HTML content optimized for Telegraph

        """
        html = self._processor.convert(markdown_text)
        optimized_html = self._optimize_for_telegraph(html)
        return optimized_html

    def convert_with_metadata(self, markdown_text: str) -> dict[str, Any]:
        """Convert markdown and extract metadata.

        Args:
        ----
            markdown_text: Markdown content with optional metadata

        Returns:
        -------
            Dictionary with HTML content and metadata

        """
        html = self.convert(markdown_text)
        return {"html": html, "metadata": self._processor.Meta}

    def _optimize_for_telegraph(self, html: str) -> str:
        """Optimize HTML for Telegraph platform.

        Args:
        ----
            html: Raw HTML content

        Returns:
        -------
            Telegraph-optimized HTML

        """
        html = self._convert_headers(html)
        html = self._optimize_code_blocks(html)
        html = self._handle_images(html)
        html = self._clean_unsupported_tags(html)
        return html

    def _convert_headers(self, html: str) -> str:
        """Convert headers to Telegraph-supported levels (h3, h4).

        Args:
        ----
            html: HTML content

        Returns:
        -------
            HTML with converted headers

        """
        # Use placeholders to avoid chain reactions
        html = re.sub(r"<h1[^>]*>", "---H1_START---", html)
        html = re.sub(r"</h1>", "---H1_END---", html)
        html = re.sub(r"<h2[^>]*>", "---H2_START---", html)
        html = re.sub(r"</h2>", "---H2_END---", html)

        # h3, h4 -> strong
        html = re.sub(r"<h[34][^>]*>", "<p><strong>", html)
        html = re.sub(r"</h[34]>", "</strong></p>", html)
        # h5, h6 -> em
        html = re.sub(r"<h[56][^>]*>", "<p><em>", html)
        html = re.sub(r"</h[56]>", "</em></p>", html)

        # Replace placeholders with final tags
        html = html.replace("---H1_START---", "<h3>")
        html = html.replace("---H1_END---", "</h3>")
        html = html.replace("---H2_START---", "<h4>")
        html = html.replace("---H2_END---", "</h4>")

        return html

    def _optimize_code_blocks(self, html: str) -> str:
        """Optimize code blocks for Telegraph.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            HTML with optimized code blocks

        """
        return html.replace('<div class="highlight">', "").replace("</div>", "")

    def _handle_images(self, html: str) -> str:
        """Process images for Telegraph compatibility.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            HTML with processed images

        """

        def process_img(match):
            img_tag = match.group(0)
            soup = BeautifulSoup(img_tag, "html.parser")
            img = soup.find("img")
            if img:
                return (
                    f"<figure><img src='{img.get('src', '')}' "
                    f"alt='{img.get('alt', '')}'><figcaption>"
                    f"{img.get('title', '')}</figcaption></figure>"
                )
            return img_tag

        return re.sub(r"<img[^>]+>", process_img, html)

    def _clean_unsupported_tags(self, html: str) -> str:
        """Remove unsupported HTML tags while preserving content.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            Cleaned HTML content

        """

        def clean_tag(match):
            return match.group(1)

        unsupported_tags = ["div", "span", "table", "tbody", "thead", "tr", "td", "th"]
        for tag in unsupported_tags:
            html = re.sub(rf"<{tag}[^>]*>(.*?)</{tag}>", clean_tag, html, flags=re.DOTALL)

        return html
