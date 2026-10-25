from unittest.mock import Mock

import httpx
import pytest
from pydantic import ValidationError

from app import title_extraction
from app.models import VideoMetadata


def test_get_video_title_reads_youtube_oembed(monkeypatch: pytest.MonkeyPatch) -> None:
    response = Mock()
    response.json.return_value = {
        "title": "Async Python Explained",
        "author_name": "Example Channel",
        "other_field": "ignored",
    }
    get = Mock(return_value=response)
    monkeypatch.setattr(title_extraction.httpx, "get", get)

    result = title_extraction.get_video_title("abc123")

    assert result == VideoMetadata(
        title="Async Python Explained",
        author="Example Channel",
        url="https://www.youtube.com/watch?v=abc123",
    )
    get.assert_called_once_with(
        "https://www.youtube.com/oembed",
        params={
            "url": "https://www.youtube.com/watch?v=abc123",
            "format": "json",
        },
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()
    response.json.assert_called_once_with()


def test_get_video_title_propagates_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    request = httpx.Request("GET", "https://www.youtube.com/oembed")
    response = httpx.Response(404, request=request)
    get = Mock(return_value=response)
    monkeypatch.setattr(title_extraction.httpx, "get", get)

    with pytest.raises(httpx.HTTPStatusError):
        title_extraction.get_video_title("missing")

    get.assert_called_once()


def test_get_video_title_requires_nonempty_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = Mock()
    response.json.return_value = {"title": "", "author_name": "A channel"}
    monkeypatch.setattr(title_extraction.httpx, "get", Mock(return_value=response))

    with pytest.raises(ValidationError):
        title_extraction.get_video_title("abc123")
