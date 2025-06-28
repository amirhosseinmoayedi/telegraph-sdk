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
        html = self._convert_strong_and_em(html)
        html = self._autolink_urls(html)
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
        # h1 -> h3, h2 -> h4
        html = re.sub(r"<h1[^>]*>", "<h3>", html)
        html = re.sub(r"</h1>", "</h3>", html)
        html = re.sub(r"<h2[^>]*>", "<h4>", html)
        html = re.sub(r"</h2>", "</h4>", html)

        # h3, h4, h5, h6 -> strong
        html = re.sub(r"<h[3-6][^>]*>", "<p><strong>", html)
        html = re.sub(r"</h[3-6]>", "</strong></p>", html)

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
        return html.replace('<div class="highlight">', "<pre>").replace("</div>", "</pre>")

    def _handle_images(self, html: str) -> str:
        """Process images for Telegraph compatibility.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            HTML with processed images

        """
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all('img'):
            parent = img.parent
            # Check if image is wrapped in a <p> tag and is the only element
            is_lonely_image = (
                parent.name == 'p' and
                all(c == img or (isinstance(c, str) and c.strip() == '') for c in parent.contents)
            )
            if is_lonely_image:
                figure = soup.new_tag('figure')
                # Create a new img tag without the 'alt' attribute
                img_clone = soup.new_tag('img', src=img.get('src', ''))
                figure.append(img_clone)
                # Create a figcaption using the alt text
                figcaption = soup.new_tag('figcaption')
                caption_text = img.get('title', img.get('alt', ''))
                figcaption.string = caption_text
                figure.append(figcaption)
                # Replace the original <p> tag with the new <figure>
                parent.replace_with(figure)
        # Return only the body content to avoid extra html/body tags
        if soup.body:
            return soup.body.decode_contents()
        return str(soup)

    def _autolink_urls(self, html: str) -> str:
        """Finds URLs in plain text and converts them to HTML links."""
        soup = BeautifulSoup(html, 'html.parser')
        text_nodes = soup.find_all(string=True)
        url_pattern = re.compile(r'(https?://[\S]+)')

        for node in text_nodes:
            # Avoid linking inside existing links, preformatted text, or code
            if node.parent.name in ['a', 'pre', 'code']:
                continue

            text = str(node)
            # Simple check to avoid processing text without URLs
            if 'http' not in text:
                continue

            # Replace URLs with anchor tags
            new_text = url_pattern.sub(r'<a href="\1">\1</a>', text)

            # If changes were made, replace the node with the new parsed HTML
            if new_text != text:
                node.replace_with(BeautifulSoup(new_text, 'html.parser'))

        # Return only the body content to avoid extra html/body tags
        if soup.body:
            return soup.body.decode_contents()
        return str(soup)

    def _convert_strong_and_em(self, html: str) -> str:
        """Convert strong and em tags to Telegraph-supported HTML.

        Args:
        ----
            html: HTML content

        Returns:
        -------
            HTML with converted strong and em tags

        """
        html = re.sub(r"<strong>", "<b>", html)
        html = re.sub(r"</strong>", "</b>", html)
        html = re.sub(r"<em>", "<i>", html)
        html = re.sub(r"</em>", "</i>", html)
        return html

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

        unsupported_tags = ["div", "span", "table", "tbody", "thead", "tr", "td", "th", "video"]
        for tag in unsupported_tags:
            html = re.sub(rf"<{tag}[^>]*>(.*?)</{tag}>", clean_tag, html, flags=re.DOTALL)

        return html
