import urllib.parse

import googleapiclient.discovery
import googleapiclient.errors

import cache
import throttling

_API_SERVICE_NAME = "youtube"
_API_VERSION = "v3"
_API_DOMAINS = ["youtube.com", "www.youtube.com", "youtu.be"]
_API_SHORTS_PATH = "shorts"
_API_WATCH_PATH = "watch"
_API_WATCH_QUERY = "v"


def _is_youtube_link(parsed: urllib.parse.ParseResult) -> bool:
    return parsed.hostname in _API_DOMAINS


def _try_extract_id_from_shorts(parsed: urllib.parse.ParseResult) -> str | None:
    path_parts = parsed.path.split("/")
    if len(path_parts) == 3 and path_parts[1] == _API_SHORTS_PATH:
        return path_parts[2]
    return None


def _try_extract_id_from_watch(parsed: urllib.parse.ParseResult) -> str | None:
    path_parts = parsed.path.split("/")
    if len(path_parts) == 2 and path_parts[1] == _API_WATCH_PATH:
        query = urllib.parse.parse_qs(parsed.query)
        if _API_WATCH_QUERY in query:
            return query[_API_WATCH_QUERY][0]

    return None


def _try_extract_id_from_short_link(parsed: urllib.parse.ParseResult) -> str | None:
    path_parts = parsed.path.split("/")
    if len(path_parts) == 2 and path_parts[1] != _API_WATCH_PATH:
        return path_parts[1]

    return None


def _try_extract_video_id(parsed: urllib.parse.ParseResult) -> str | None:
    yield _try_extract_id_from_shorts(parsed)
    yield _try_extract_id_from_watch(parsed)
    yield _try_extract_id_from_short_link(parsed)


def parse_video_id_by_link(link: str) -> str | None:
    parsed = urllib.parse.urlparse(link)
    if _is_youtube_link(parsed):
        for video_id in _try_extract_video_id(parsed):
            if video_id:
                return video_id

    return None


def _filter_owner_comments(_thread: dict, _chanel_id) -> list[str]:
    _comments = []
    for item in _thread.get("items", []):
        top_level_comment = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
        if text := top_level_comment.get("textOriginal"):
            comment_owner = top_level_comment.get('authorChannelId', {}).get('value', '')
            if _chanel_id == comment_owner:
                _comments.append(text)

    return _comments


class VideoSummary:
    video_id: str
    chanel_id: str
    title: str
    description: str | None
    owner_comments: list[str]
    relevant_comments: list[str]

    def __init__(self, _video_id: str,
                 _chanel_id: str,
                 _title: str,
                 _description: str | None,
                 _owner_comments: list[str],
                 _relevant_comments: list[str]
                 ):
        self.video_id = _video_id
        self.chanel_id = _chanel_id
        self.title = _title
        self.description = _description
        self.owner_comments = _owner_comments
        self.relevant_comments = _relevant_comments


class Api:
    _youtube = None
    _limiter = None
    _cache = None

    def __init__(self, api_key, limiter: throttling.RateLimiter, storage: cache.Storage):
        self._youtube = googleapiclient.discovery.build(
            _API_SERVICE_NAME, _API_VERSION, developerKey=api_key
        )
        self._limiter = limiter
        self._cache = storage

    def get_video_summary_by_id(self, video_id: str, max_comments: int) -> VideoSummary | None:
        try:
            chanel_id = self.parse_video_data(video_id, "channelId")

            return VideoSummary(
                video_id,
                chanel_id,
                self.parse_video_data(video_id, "title"),
                self.parse_video_data(video_id, "description"),
                self.parse_owner_comments(video_id, chanel_id),
                self.parse_video_comments(video_id, max_comments)
            )
        except YoutubeException as e:
            print({
                "video_id": video_id,
                "reason": e.reason,
                "code": e.code
            })
            return None

    def parse_video_data(self, video_id: str, snippet_property: str = None):
        video = self._fetch_video(video_id)
        for item in video.get("items", []):
            snippet = item.get("snippet", {})
            if snippet_property is None:
                return snippet
            elif snippet_property in snippet:
                return snippet[snippet_property]

        return ""

    def parse_owner_comments(self, video_id, channel_id, max_comments=100) -> list[str]:
        comments = _filter_owner_comments(self._fetch_comments(video_id, max_comments), channel_id)

        if len(comments) == 0:
            comments = _filter_owner_comments(self._fetch_comments(video_id, max_comments, "time"), channel_id)

        return comments

    def parse_video_comments(self, video_id, max_comments) -> list[str]:
        comments = []
        thread = self._fetch_comments(video_id, max_comments)
        for item in thread.get("items", []):
            top_level_comment = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            if text := top_level_comment.get("textOriginal"):
                comments.append(text)

        return comments

    def _fetch_video(self, video_id: str) -> dict:
        try:
            return self._execute_list("videos",
                                      part="snippet",
                                      id=video_id)
        except googleapiclient.errors.HttpError as e:
            raise YoutubeException(e.reason, e.status_code)

    def _fetch_comments(self, video_id: str, max_comments, order="relevance") -> dict:
        try:
            return self._execute_list("commentThreads",
                                      part="snippet",
                                      order=order,
                                      videoId=video_id,
                                      maxResults=max_comments)
        except googleapiclient.errors.HttpError:
            return {}

    def _fetch_owner_comments(self, video_id, channel_id) -> dict:
        try:
            return self._execute_list("commentThreads",
                                      part="snippet",
                                      order="relevance",
                                      videoId=video_id,
                                      allThreadsRelatedToChannelId=channel_id)
        except googleapiclient.errors.HttpError as e:
            return {}

    def _execute_list(self, section, **kwargs):
        @cache.with_cache(storage=self._cache)
        def fetch_data(_section, **_kwargs):
            request = getattr(self._youtube, _section)().list(
                **_kwargs
            )

            return self._execute_request(request)

        return fetch_data(section, **kwargs)

    def _execute_request(self, request) -> dict:
        @throttling.with_limiter(limiter=self._limiter)
        def execute(_request):
            return _request.execute()

        return execute(request)


class YoutubeException(Exception):
    reason: str
    code: int

    def __init__(self, reason: str, code: int):
        self.reason = reason
        self.code = code
