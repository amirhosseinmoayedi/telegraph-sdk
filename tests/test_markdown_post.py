import os

import pytest

from telegraph import TelegraphClient
from telegraph.core.models import PageContent

TELEGRAPH_TOKEN = os.environ.get("TELEGRAPH_TOKEN")


def test_markdown_conversion():
    """Test markdown to HTML conversion."""
    client = TelegraphClient()
    markdown_content = (
        "# H1\n"
        "## H2\n"
        "### H3\n"
        "#### H4\n"
        "##### H5\n"
        "###### H6"
    )
    html_content = client.markdown.convert(markdown_content)

    expected_html = (
        "<h3>H1</h3>"
        "<h4>H2</h4>"
        "<p><strong>H3</strong></p>"
        "<p><strong>H4</strong></p>"
        "<p><em>H5</em></p>"
        "<p><em>H6</em></p>"
    )
    assert "".join(html_content.split()) == expected_html


@pytest.mark.asyncio
@pytest.mark.skipif(not TELEGRAPH_TOKEN, reason="TELEGRAPH_TOKEN not set in environment")
async def test_create_markdown_post_api():
    """Test creating a page with markdown content via API."""
    client = TelegraphClient(access_token=TELEGRAPH_TOKEN)
    title = "Test Markdown Post (pytest)"
    markdown_content = (
        "# Pytest Markdown Post\n\n"
        "This is a **pytest** _markdown_ post!\n\n"
        "- Item 1\n"
        "- Item 2\n\n"
        "[Telegraph](https://telegra.ph)"
    )
    html_content = client.markdown.convert(markdown_content)
    page_content = PageContent(
        title=title,
        content=html_content,
        author_name="Pytest Bot",
        author_url="https://github.com/amirhosseinmoayedi/telegraph-sdk",
        content_type="html",
    )
    page = await client.create_page(page_content)
    assert page.url.startswith("https://telegra.ph/")
    assert page.title == title
    print(f"Created page: {page.url}")
