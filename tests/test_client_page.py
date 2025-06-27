import os
import pytest
from telegraph import TelegraphClient
from telegraph.core.models import PageContent

TELEGRAPH_TOKEN = os.environ.get("TELEGRAPH_TOKEN")

@pytest.mark.asyncio
@pytest.mark.skipif(not TELEGRAPH_TOKEN, reason="TELEGRAPH_TOKEN not set in environment")
async def test_create_and_edit_page():
    client = TelegraphClient(access_token=TELEGRAPH_TOKEN)
    title = "Test Page"
    html_content = "<p>Hello <b>Telegraph</b>!</p>"
    page_content = PageContent(title=title, content=html_content, content_type="html")
    page = await client.create_page(page_content)
    assert page.url.startswith("https://telegra.ph/")
    assert page.title == title

    # Edit the page
    new_title = "Updated Test Page"
    new_content = "<p>Updated content</p>"
    updated_content = PageContent(title=new_title, content=new_content, content_type="html")
    updated_page = await client.edit_page(page.path, updated_content)
    assert updated_page.title == new_title
    assert updated_page.can_edit

@pytest.mark.asyncio
@pytest.mark.skipif(not TELEGRAPH_TOKEN, reason="TELEGRAPH_TOKEN not set in environment")
async def test_get_page():
    client = TelegraphClient(access_token=TELEGRAPH_TOKEN)
    # Create a page first
    page_content = PageContent(title="Get Page Test", content="<p>Get me!</p>", content_type="html")
    page = await client.create_page(page_content)
    got_page = await client.get_page(page.path)
    assert got_page.title == "Get Page Test"
    assert got_page.url == page.url
