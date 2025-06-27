import os
import pytest
import asyncio
from telegraph import TelegraphClient

TELEGRAPH_TOKEN = os.environ.get("TELEGRAPH_TOKEN")

@pytest.mark.asyncio
@pytest.mark.skipif(not TELEGRAPH_TOKEN, reason="TELEGRAPH_TOKEN not set in environment")
async def test_create_markdown_post():
    client = TelegraphClient(access_token=TELEGRAPH_TOKEN)
    title = "Test Markdown Post (pytest)"
    markdown_content = """
# Pytest Markdown Post\n\nThis is a **pytest** _markdown_ post!\n\n- Item 1\n- Item 2\n\n[Telegraph](https://telegra.ph)
"""
    html_content = client.markdown.convert(markdown_content)
    from telegraph.core.models import PageContent
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
