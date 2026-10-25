import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app import main as main_module
from app.models import VideoMetadata


def test_generate_summary_saves_markdown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    subtitles = [{"text": "Hello world", "start": 10.0, "duration": 2.0}]
    transcript = SimpleNamespace(to_raw_data=Mock(return_value=subtitles))
    fetch = Mock(return_value=transcript)
    api_class = Mock(return_value=SimpleNamespace(fetch=fetch))
    get_metadata = Mock(
        return_value=VideoMetadata(
            title="FastAPI Crash Course",
            author="Example Channel",
            url="https://www.youtube.com/watch?v=abc123",
        )
    )
    summarize = Mock(return_value="# Video Summary\n\nUseful notes.")

    monkeypatch.setattr(main_module, "YouTubeTranscriptApi", api_class)
    monkeypatch.setattr(main_module, "get_video_title", get_metadata)
    monkeypatch.setattr(main_module, "summarize_transcript", summarize)

    result = main_module.generate_summary("abc123")

    assert result == Path("output/fastapi-crash-course.md")
    assert result.exists()
    assert result.read_text(encoding="utf-8") == (
        "**Video:** FastAPI Crash Course\n"
        "**Channel:** Example Channel\n"
        "**Source:** https://www.youtube.com/watch?v=abc123\n\n"
        "---\n\n"
        "# Video Summary\n\nUseful notes.\n"
    )
    api_class.assert_called_once_with()
    fetch.assert_called_once_with("abc123")
    transcript.to_raw_data.assert_called_once_with()
    get_metadata.assert_called_once_with("abc123")
    summarize.assert_called_once_with(subtitles)


def test_generate_summary_falls_back_to_video_id_for_empty_slug(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        main_module,
        "YouTubeTranscriptApi",
        lambda: SimpleNamespace(fetch=lambda _video_id: SimpleNamespace(to_raw_data=lambda: [])),
    )
    monkeypatch.setattr(
        main_module,
        "get_video_title",
        lambda _video_id: VideoMetadata(title="!!!", author="Channel", url="https://example.com/watch?v=abc123"),
    )
    monkeypatch.setattr(main_module, "summarize_transcript", lambda _subs: "Notes")

    result = main_module.generate_summary("abc123")

    assert result == Path("output/abc123.md")
    assert result.read_text(encoding="utf-8").endswith("Notes\n")


@pytest.mark.parametrize("argv", [["app.main"], ["app.main", "first", "second"]])
def test_main_rejects_wrong_number_of_arguments(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", argv)

    with pytest.raises(SystemExit, match="Usage: python -m app.main <video_id>"):
        main_module.main()


def test_main_prints_saved_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "lecture.md"
    generate = Mock(return_value=target)
    monkeypatch.setattr(sys, "argv", ["app.main", "abc123"])
    monkeypatch.setattr(main_module, "generate_summary", generate)

    main_module.main()

    generate.assert_called_once_with("abc123")
    assert capsys.readouterr().out == f"Saved to: {target.resolve()}\n"
