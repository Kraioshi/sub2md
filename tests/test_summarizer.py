import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app import summarizer


def test_summarize_transcript_sends_transcript_and_returns_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    subtitles = [{"text": "Привет, Python!", "start": 62.5, "duration": 3.0}]
    response = SimpleNamespace(output_text="# Video Summary\nHello", usage=None)
    create = Mock(return_value=response)
    client_class = Mock(return_value=SimpleNamespace(responses=SimpleNamespace(create=create)))
    load_dotenv = Mock()
    monkeypatch.setattr(summarizer, "OpenAI", client_class)
    monkeypatch.setattr(summarizer, "load_dotenv", load_dotenv)

    result = summarizer.summarize_transcript(subtitles)

    assert result == "# Video Summary\nHello"
    load_dotenv.assert_called_once_with()
    client_class.assert_called_once_with()
    create.assert_called_once()
    kwargs = create.call_args.kwargs
    assert kwargs["model"] == "gpt-4.1-mini"
    assert kwargs["temperature"] == 0.2
    assert kwargs["instructions"] == summarizer.SYSTEM_PROMPT
    assert kwargs["input"].startswith(summarizer.USER_PROMPT)
    transcript_json = kwargs["input"].split("<transcript>\n", 1)[1].split("\n</transcript>", 1)[0]
    assert json.loads(transcript_json) == subtitles
    assert "Привет" in transcript_json  # Non-ASCII text is not escaped.


@pytest.mark.parametrize("output_text", ["", "   \n  "])
def test_summarize_transcript_rejects_empty_model_output(output_text: str, monkeypatch: pytest.MonkeyPatch) -> None:
    response = SimpleNamespace(output_text=output_text, usage=None)
    create = Mock(return_value=response)
    monkeypatch.setattr(summarizer, "load_dotenv", Mock())
    monkeypatch.setattr(
        summarizer,
        "OpenAI",
        Mock(return_value=SimpleNamespace(responses=SimpleNamespace(create=create))),
    )

    with pytest.raises(ValueError, match="OpenAI returned an empty summary"):
        summarizer.summarize_transcript([])


def test_summarize_transcript_reports_token_usage(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    response = SimpleNamespace(
        output_text="Notes",
        usage=SimpleNamespace(input_tokens=10, output_tokens=5, total_tokens=15),
    )
    monkeypatch.setattr(summarizer, "load_dotenv", Mock())
    monkeypatch.setattr(
        summarizer,
        "OpenAI",
        Mock(return_value=SimpleNamespace(responses=SimpleNamespace(create=Mock(return_value=response)))),
    )

    result = summarizer.summarize_transcript([])

    assert result == "Notes"
    assert capsys.readouterr().out == ("Input tokens: 10\nOutput tokens: 5\nTotal tokens: 15\n")
