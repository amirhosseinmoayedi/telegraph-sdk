"""Batch file upload functionality."""

import asyncio
from pathlib import Path
from typing import Callable, Optional, Union

from telegraph.core.models import UploadResult
from telegraph.upload.file_handler import FileUploader


class BatchUploader:
    """Batch file uploader for Telegraph."""

    def __init__(self, uploader: FileUploader, max_concurrent: int = 5) -> None:
        """Initialize batch uploader.

        Args:
        ----
            uploader: File uploader instance
            max_concurrent: Maximum concurrent uploads

        """
        self._uploader = uploader
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def upload_files(
        self,
        file_paths: list[Union[str, Path]],
        progress_callback: Optional[Callable[[int, int, UploadResult], None]] = None,
    ) -> list[UploadResult]:
        """Upload multiple files concurrently.

        Args:
        ----
            file_paths: List of file paths
            progress_callback: Progress callback (current, total, result)

        Returns:
        -------
            List of upload results

        """
        tasks = [
            self._upload_with_semaphore(path, i, len(file_paths), progress_callback)
            for i, path in enumerate(file_paths)
        ]
        return await asyncio.gather(*tasks)

    async def _upload_with_semaphore(
        self,
        file_path: Union[str, Path],
        index: int,
        total: int,
        progress_callback: Optional[Callable[[int, int, UploadResult], None]] = None,
    ) -> UploadResult:
        """Upload file with semaphore control.

        Args:
        ----
            file_path: Path to file
            index: Current file index
            total: Total files
            progress_callback: Progress callback

        Returns:
        -------
            Upload result

        """
        async with self._semaphore:
            result = await self._uploader.upload_file(file_path)
            if progress_callback:
                progress_callback(index + 1, total, result)
            return result
