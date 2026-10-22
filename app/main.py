import sys
from pathlib import Path

from slugify import slugify
from youtube_transcript_api import YouTubeTranscriptApi

from app.summarizer import summarize_transcript
from app.title_extraction import get_video_title


def generate_summary(video_id: str) -> Path:
    transcript = YouTubeTranscriptApi().fetch(video_id)
    metadata = get_video_title(video_id)

    summary = summarize_transcript(transcript.to_raw_data())

    filename = (
        slugify(
            metadata.title,
            max_length=100,
            word_boundary=True,
            algorithm="modern",
        )
        or video_id
    )

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"{filename}.md"

    content = (
        f"**Video:** {metadata.title}\n**Channel:** {metadata.author}\n**Source:** {metadata.url}\n\n---\n\n{summary}\n"
    )

    file_path.write_text(content, encoding="utf-8")

    return file_path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m app.main <video_id>")

    video_id = sys.argv[1]
    file_path = generate_summary(video_id)

    print(f"Saved to: {file_path.resolve()}")


if __name__ == "__main__":
    main()
