"""Azure Blob Storage utilities for persisting downloaded audio."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContentSettings


class AzureBlobStorageError(RuntimeError):
    """Raised when the Azure Blob storage backend is misconfigured."""


@dataclass
class AzureBlobStorageConfig:
    """Configuration required to interact with Azure Blob Storage."""

    container_name: str
    root_path: str = "playlists"
    connection_string: Optional[str] = None
    account_url: Optional[str] = None
    credential: Optional[str] = None

    @classmethod
    def from_env(cls) -> "AzureBlobStorageConfig":
        """Create configuration from environment variables."""

        container = os.getenv("AZURE_BLOB_CONTAINER")
        if not container:
            raise AzureBlobStorageError(
                "Missing AZURE_BLOB_CONTAINER environment variable."
            )

        root_path = os.getenv("AZURE_BLOB_ROOT_PATH", "playlists")

        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if connection_string:
            return cls(
                container_name=container,
                root_path=root_path,
                connection_string=connection_string,
            )

        account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
        if not account_url:
            raise AzureBlobStorageError(
                "Provide either AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_URL."
            )

        credential = (
            os.getenv("AZURE_STORAGE_SAS_TOKEN")
            or os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        )
        if not credential:
            raise AzureBlobStorageError(
                "Provide AZURE_STORAGE_SAS_TOKEN or AZURE_STORAGE_ACCOUNT_KEY when using account URL."
            )

        return cls(
            container_name=container,
            root_path=root_path,
            account_url=account_url,
            credential=credential,
        )


class AzureBlobStorage:
    """Simple wrapper around Azure Blob Storage uploads."""

    def __init__(self, config: AzureBlobStorageConfig) -> None:
        self.config = config
        if config.connection_string:
            self._service_client = BlobServiceClient.from_connection_string(
                config.connection_string
            )
        else:
            assert config.account_url is not None
            self._service_client = BlobServiceClient(
                account_url=config.account_url,
                credential=config.credential,
            )
        self._container_client = self._service_client.get_container_client(
            config.container_name
        )
        self._ensure_container_exists()

    @classmethod
    def from_env(cls) -> "AzureBlobStorage":
        return cls(AzureBlobStorageConfig.from_env())

    def _ensure_container_exists(self) -> None:
        try:
            self._container_client.create_container()
        except ResourceExistsError:
            return

    def build_blob_name(
        self, playlist_id: str, query_type: str, source_file: Path
    ) -> str:
        """Construct a blob name for a downloaded file."""

        parts = [
            self.config.root_path.strip("/"),
            playlist_id,
            query_type,
            source_file.name,
        ]
        return "/".join(part for part in parts if part)

    def upload_file(
        self, playlist_id: str, query_type: str, local_path: Path
    ) -> str:
        """Upload a local file and return the blob URL."""

        blob_name = self.build_blob_name(playlist_id, query_type, local_path)
        blob_client = self._container_client.get_blob_client(blob_name)
        content_settings = ContentSettings(content_type="audio/mpeg")
        with local_path.open("rb") as file_handle:
            blob_client.upload_blob(file_handle, overwrite=True, content_settings=content_settings)
        return blob_client.url

    def blob_exists(self, blob_name: str) -> bool:
        return self._container_client.get_blob_client(blob_name).exists()
