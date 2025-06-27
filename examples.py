import asyncio
import os
from pathlib import Path

# This assumes the 'telegraph' package is in the same directory or installed.
from telegraph import TelegraphAPIError, TelegraphClient, ValidationError


async def basic_usage():
    """Demonstrates basic client usage."""
    print("=== Running Basic Usage Example ===")
    client = TelegraphClient()
    try:
        # Create a new account
        account = await client.create_account("MyTestAccount")
        print(f"Created account: {account.short_name}")
        print(f"Access Token: {account.access_token}")

        # Use the new account's token for future sessions
        client_with_token = TelegraphClient(access_token=account.access_token)

        # Create a new page
        page_content = "<p>Hello, world! This is a test page.</p>"
        page = await client_with_token.create_page("Test Page", page_content)
        print(f"Created page: {page.url}")

        # Get the page content
        retrieved_page = await client_with_token.get_page(page.path)
        print(f"Retrieved page title: {retrieved_page.title}")

    except TelegraphAPIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


async def advanced_content_processing():
    """Demonstrates advanced content processing with Markdown."""
    print("\n=== Running Advanced Content Processing Example ===")
    client = TelegraphClient()
    try:
        account = await client.create_account("MarkdownDemo")
        client_with_token = TelegraphClient(access_token=account.access_token)

        markdown_text = """
# My Markdown Page

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2

```python
print("Hello, Markdown!")
```
"""

        # Convert markdown to HTML
        html_content = client.markdown.convert(markdown_text)

        # Create page with processed markdown
        page = await client_with_token.create_page("Markdown Page", html_content)
        print(f"Created Markdown page: {page.url}")

    except TelegraphAPIError as e:
        print(f"API Error: {e}")


async def batch_operations():
    """Demonstrates batch file uploading."""
    print("\n=== Running Batch Operations Example ===")
    # Create dummy image files for testing
    Path("test_images").mkdir(exist_ok=True)
    image_paths = []
    for i in range(3):
        path = Path(f"test_images/image_{i}.png")
        path.touch()
        image_paths.append(path)

    client = TelegraphClient()
    try:

        def progress_callback(current, total, result):
            print(f"Uploaded {current}/{total}: {result.url or result.error}")

        results = await client.uploader.batch_upload(image_paths, progress_callback)
        print("\nBatch upload complete.")
        for res in results:
            if res.success:
                print(f"Success: {res.url}")
            else:
                print(f"Error: {res.error}")

    except Exception as e:
        print(f"An error occurred during batch upload: {e}")
    finally:
        # Clean up dummy files
        for path in image_paths:
            os.remove(path)
        os.rmdir("test_images")


async def error_handling_example():
    """Demonstrates error handling for API and validation errors."""
    print("\n=== Running Error Handling Example ===")
    client = TelegraphClient(access_token="invalid-token") # noqa: S106
    try:
        # This will fail due to invalid token
        await client.get_account_info()
    except TelegraphAPIError as e:
        print(f"Caught expected API error: {e.message}")

    try:
        # This will fail due to invalid title
        await client.create_page("", "<p>content</p>")
    except ValidationError as e:
        print(f"Caught expected validation error: {e.field} - {e.message}")


async def content_validation_example():
    """Demonstrates content validation and sanitization."""
    print("\n=== Running Content Validation Example ===")
    client = TelegraphClient()

    # Example of invalid HTML that will be sanitized
    dirty_html = (
        '<p>This is clean. <script>alert("XSS")</script>'
        '<div style="color:red">And this is a div.</div></p>'
    )
    sanitized_html = client.content_validator.sanitize_html(dirty_html)

    print(f"Original HTML: {dirty_html}")
    print(f"Sanitized HTML: {sanitized_html}")


async def comprehensive_analytics():
    """Demonstrates comprehensive analytics features."""
    print("\n=== Running Comprehensive Analytics Example ===")
    try:
        client = TelegraphClient()
        account = await client.create_account("AnalyticsTest")
        client = TelegraphClient(access_token=account.access_token)

        # Create a few pages to get stats for
        await client.create_page("Analytics Page 1", "<p>Content 1</p>")
        await client.create_page("Analytics Page 2", "<p>Content 2</p>")

        # Get account summary
        summary = await client.analytics.get_account_summary()
        print(f"Total pages: {summary['total_pages']}")
        print(f"Total views: {summary['total_views']}")

        if summary["top_pages"]:
            top_page_path = summary["top_pages"][0]["path"]
            print(
                f"Top page: {summary['top_pages'][0]['title']} "
                f"with {summary['top_pages'][0]['views']} views"
            )

            # Deep analytics for top page
            analytics = await client.analytics.get_page_analytics(top_page_path, days_back=30)

            print(f"\n=== Analytics for '{summary['top_pages'][0]['title']}' ===")
            print(f"Total Views: {analytics['total'].views}")
            print(f"This Year: {analytics['yearly'].views}")
            print(f"This Month: {analytics['monthly'].views}")

            if "daily" in analytics:
                recent_days = analytics["daily"][:7]  # Last 7 days
                print("\nLast 7 Days:")
                for day_data in recent_days:
                    print(f"  {day_data['date']}: {day_data['views']} views")

        # Compare top pages
        MIN_TOP_PAGES_FOR_COMPARISON = 2
        if len(summary["top_pages"]) >= MIN_TOP_PAGES_FOR_COMPARISON:
            top_paths = [p["path"] for p in summary["top_pages"][:3]]
            comparison = await client.analytics.compare_pages(top_paths)

            print("\n=== Page Comparison ===")
            for path, data in comparison.items():
                if "error" not in data:
                    print(f"{data['title']}: {data['views']} views")
                else:
                    print(f"{path}: Error - {data['error']}")

    except Exception as e:
        print(f"Analytics error: {e}")


if __name__ == "__main__":
    # Run advanced examples
    asyncio.run(advanced_content_processing())
    # asyncio.run(batch_operations())  # Uncomment if you have image files
    asyncio.run(error_handling_example())
    asyncio.run(content_validation_example())
