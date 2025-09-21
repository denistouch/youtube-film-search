import time

import googleapiclient.discovery

_youtube = None
_cache = dict()
_last_request = None

_API_SERVICE_NAME = "youtube"
_API_VERSION = "v3"
_REQUEST_COMMENT_THREADS = 'commentThreads'
_REQUEST_VIDEOS = 'videos'


def init_service(key):
    global _youtube

    _youtube = googleapiclient.discovery.build(
        _API_SERVICE_NAME, _API_VERSION, developerKey=key
    )


def parse_video_data(video_id: str, snippet_property: str) -> str:
    video = _fetch_video(video_id)
    for item in video.get('items', []):
        snippet = item.get('snippet', {})
        if snippet_property in snippet:
            return snippet[snippet_property]

    return ''


def parse_video_comments(video_id) -> list[str]:
    comments = []
    thread = _fetch_comments(video_id)
    for item in thread.get('items', []):
        if text := item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {}).get('textOriginal'):
            comments.append(text)

    return comments


def _fetch_video(video_id: str) -> dict:
    request = _youtube.videos().list(
        part="snippet",
        id=video_id
    )

    return _execute_request_cached(request, video_id, _REQUEST_VIDEOS)


def _fetch_comments(video_id: str) -> dict:
    request = _youtube.commentThreads().list(
        part="snippet",
        order="relevance",
        videoId=video_id
    )

    return _execute_request_cached(request, video_id, _REQUEST_COMMENT_THREADS)


def _with_throttling(func):
    def wrapper(*args, **kwargs):
        global _last_request
        if isinstance(_last_request, float):
            now = time.time()
            if (now - _last_request) < 1:
                time.sleep(now - _last_request)

        result = func(*args, **kwargs)
        _last_request = time.time()

        return result

    return wrapper


@_with_throttling
def _execute_request_cached(request, request_key, request_type) -> dict:
    cached = _cache_get(request_key, request_type)

    if cached is not None:
        return cached

    response = request.execute()
    _cache_put(request_key, request_type, response)

    return response


def _cache_put(video_id: str, type_cache: str, data):
    _cache.setdefault(video_id, {})[type_cache] = data


def _cache_get(video_id: str, type_cache: str, default_value=None):
    return _cache.get(video_id, {}).get(type_cache, default_value)
