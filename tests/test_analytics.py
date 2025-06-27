import os
import pytest
from telegraph import TelegraphClient
from telegraph.core.models import PageContent

TELEGRAPH_TOKEN = os.environ.get("TELEGRAPH_TOKEN")

@pytest.mark.asyncio
@pytest.mark.skipif(not TELEGRAPH_TOKEN, reason="TELEGRAPH_TOKEN not set in environment")
async def test_analytics_views():
    client = TelegraphClient(access_token=TELEGRAPH_TOKEN)
    # Create a page to get stats on
    page_content = PageContent(title="Analytics Test", content="<p>Stats!</p>", content_type="html")
    page = await client.create_page(page_content)
    stats = await client.analytics.get_views(page.path)
    assert stats.views >= 0
