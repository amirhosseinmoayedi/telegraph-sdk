"""Async file uploader for Telegraph."""

from pathlib import Path
from typing import Callable, ClassVar, Optional, Union

import aiohttp
from core.models import UploadResult

HTTP_OK = 200


class FileUploader:
    """Async file uploader for Telegraph."""

    ALLOWED_EXTENSIONS: ClassVar[set[str]] = {".jpg", ".jpeg", ".png", ".gif", ".mp4"}
    MAX_FILE_SIZE: int = 50 * 1024 * 1024

    def __init__(self, domain: str = "telegra.ph", timeout: int = 30) -> None:
        """Initialize file uploader.

        Args:
        ----
            domain: Telegraph domain
            timeout: Upload timeout in seconds

        """
        self._domain = domain
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def upload_file(
        self,
        file_path: Union[str, Path],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> UploadResult:
        """Upload single file to Telegraph.

        Args:
        ----
            file_path: Path to file
            progress_callback: Progress callback function

        Returns:
        -------
            Upload result

        """
        path = Path(file_path)
        is_valid, error = self._validate_file(path)
        if not is_valid:
            return UploadResult(success=False, error=error)

        return await self._perform_upload(path, progress_callback)

    async def upload_from_bytes(
        self, file_data: bytes, filename: str, mime_type: Optional[str] = None
    ) -> UploadResult:
        """Upload file from bytes data.

        Args:
        ----
            file_data: File bytes
            filename: File name
            mime_type: MIME type

        Returns:
        -------
            Upload result

        """
        if len(file_data) > self.MAX_FILE_SIZE:
            return UploadResult(success=False, error="File size exceeds limit")

        return await self._upload_bytes(
            file_data, filename, mime_type or "application/octet-stream"
        )

    def _validate_file(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Validate file for upload.

        Args:
        ----
            file_path: Path to file

        Returns:
        -------
            Validation result

        """
        if not file_path.exists():
            return False, "File not found"
        if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            return False, "Invalid file type"
        if file_path.stat().st_size > self.MAX_FILE_SIZE:
            return False, "File size exceeds limit"
        return True, None

    async def _perform_upload(
        self,
        file_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> UploadResult:
        """Perform file upload.

        Args:
        ----
            file_path: Path to file
            progress_callback: Progress callback

        Returns:
        -------
            Upload result

        """
        url = f"https://{self._domain}/upload"

        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                with open(file_path, "rb") as f:
                    data = aiohttp.FormData()
                    data.add_field("file", f, filename=file_path.name)

                    async with session.post(url, data=data) as response:
                        if response.status == HTTP_OK:
                            result = await response.json()
                            return UploadResult(success=True, url=result[0]["src"])
                        else:
                            error_text = await response.text()
                            return UploadResult(
                                success=False, error=f"Upload failed: {error_text}"
                            )
        except aiohttp.ClientError as e:
            return UploadResult(success=False, error=str(e))

    async def _upload_bytes(self, file_data: bytes, filename: str, mime_type: str) -> UploadResult:
        """Upload file from bytes.

        Args:
        ----
            file_data: File bytes
            filename: File name
            mime_type: MIME type

        Returns:
        -------
            Upload result

        """
        url = f"https://{self._domain}/upload"

        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                data = aiohttp.FormData()
                data.add_field("file", file_data, filename=filename, content_type=mime_type)

                async with session.post(url, data=data) as response:
                    if response.status == HTTP_OK:
                        result = await response.json()
                        return UploadResult(success=True, url=result[0]["src"])
                    else:
                        error_text = await response.text()
                        return UploadResult(success=False, error=f"Upload failed: {error_text}")
        except aiohttp.ClientError as e:
            return UploadResult(success=False, error=str(e))
