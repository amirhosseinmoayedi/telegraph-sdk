import os
import pytest
from telegraph import TelegraphClient

TELEGRAPH_TOKEN = os.environ.get("TELEGRAPH_TOKEN")

@pytest.mark.asyncio
@pytest.mark.skipif(not TELEGRAPH_TOKEN, reason="TELEGRAPH_TOKEN not set in environment")
async def test_get_account_info():
    client = TelegraphClient(access_token=TELEGRAPH_TOKEN)
    account = await client.get_account_info()
    assert account.short_name
    assert account.page_count is not None
    assert account.author_name is not None or account.author_url is not None

@pytest.mark.asyncio
@pytest.mark.skipif(not TELEGRAPH_TOKEN, reason="TELEGRAPH_TOKEN not set in environment")
async def test_edit_account_info():
    client = TelegraphClient(access_token=TELEGRAPH_TOKEN)
    new_name = "TestBotName"
    updated = await client.edit_account_info(short_name=new_name)
    assert updated.short_name == new_name
