import httpx

from app.models import VideoMetadata


def get_video_title(video_id: str) -> VideoMetadata:
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    response = httpx.get(
        "https://www.youtube.com/oembed",
        params={"url": video_url, "format": "json"},
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()

    return VideoMetadata(
        title=data["title"],
        author=data["author_name"],
        url=video_url,
    )
