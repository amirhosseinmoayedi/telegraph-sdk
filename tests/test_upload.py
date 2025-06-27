import os
import pytest
from telegraph import TelegraphClient

TELEGRAPH_TOKEN = os.environ.get("TELEGRAPH_TOKEN")

@pytest.mark.asyncio
@pytest.mark.skipif(not TELEGRAPH_TOKEN, reason="TELEGRAPH_TOKEN not set in environment")
async def test_file_uploader(tmp_path):
    # Download a real PNG image for upload
    import requests
    url = "https://upload.wikimedia.org/wikipedia/commons/2/2c/1x1.png"
    img_file = tmp_path / "test.png"
    r = requests.get(url, timeout=10)
    img_file.write_bytes(r.content)
    client = TelegraphClient(access_token=TELEGRAPH_TOKEN)
    result = await client.uploader.upload_file(str(img_file))
    assert result.success, f"Upload failed: {result.error}"
    assert result.url and result.url.startswith("https://telegra.ph/file/")
