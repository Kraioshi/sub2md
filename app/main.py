import sys
from pathlib import Path

from title_extraction import get_video_title
from youtube_transcript_api import YouTubeTranscriptApi

from app.slugify import slugify_text
from app.summarizer import summarize_transcript

vid_id: str = ""


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m app.main <video_id>")

    video_id = sys.argv[1]

    # Fetch the transcript and video metadata
    yttp_api = YouTubeTranscriptApi()
    transcript = yttp_api.fetch(video_id)
    metadata = get_video_title(video_id)

    # Generate the summary
    summary = summarize_transcript(transcript.to_raw_data())

    # Prepare output path
    filename = slugify_text(metadata.title)[:100] or video_id

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    file_path = output_dir / f"{filename}-{video_id}.md"

    # Save Markdown
    content = (
        f"**Video:** {metadata.title}\n**Channel:** {metadata.author}\n**Source:** {metadata.url}\n\n---\n\n{summary}\n"
    )

    file_path.write_text(content, encoding="utf-8")

    print(f"Saved to: {file_path.resolve()}")


if __name__ == "__main__":
    main()
