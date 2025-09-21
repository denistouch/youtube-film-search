import os

from dotenv import load_dotenv

import youtube_api


def main():
    load_dotenv()
    youtube_api.init_service(os.getenv("GOOGLE_API_KEY"))
    print(get_video_summary("WaV93J4X5AM"))


def get_video_summary(video_id: str) -> dict:
    return {
        'title': youtube_api.parse_video_data(video_id, 'title'),
        'comments': youtube_api.parse_video_comments(video_id)
    }


if __name__ == "__main__":
    main()
