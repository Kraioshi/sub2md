import httpx

from app.title_schema import TitleResponse


def get_video_title(video_id: str) -> TitleResponse:
    response = httpx.get(
        "https://www.youtube.com/oembed",
        params={
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "format": "json",
        },
        timeout=10,
    )
    data = response.json()

    return TitleResponse(
        title=data["title"],
        author=data["author_name"],
        url=f"https://www.youtube.com/watch?v={video_id}",
    )
