# Telegraph SDK

A comprehensive async Python package for the Telegraph API, with enhanced support for Markdown, file uploads, and analytics.

## Features

- Fully asynchronous client based on `aiohttp`.
- Advanced Markdown-to-HTML conversion.
- Batch file uploading with progress tracking.
- Rich analytics for page views.
- Clean, object-oriented design with dataclasses.
- Built-in content validation and sanitization.

## Installation

This project uses `uv` for package management. To install the dependencies, first install `uv`, then run:

```bash
uv pip install -r requirements.txt
```

Alternatively, to set up a virtual environment and install dependencies:

```bash
uv venv
uv pip sync pyproject.toml
```

## Usage

Here's a quick example of how to create a new Telegraph page:

```python
import asyncio
from telegraph import TelegraphClient

async def main():
    client = TelegraphClient()
    try:
        account = await client.create_account("MyTestAccount")
        client_with_token = TelegraphClient(access_token=account.access_token)

        page = await client_with_token.create_page(
            "Test Page",
            "<p>Hello, world! This is a test page.</p>"
        )
        print(f"Created page: {page.url}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

Check out `examples.py` for more advanced usage.
