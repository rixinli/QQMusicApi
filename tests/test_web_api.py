"""
综合 API 可用性测试 - 先 search 获取真实 ID，再测依赖接口

流程：按 search 分类获取数据 → 提取 ID → 传入对应 API
- search_type 0 歌曲 → song/*, lyric, comment/*
- search_type 1 歌手 → singer/*
- search_type 2 专辑 → album/*
- search_type 3 歌单 → songlist/*
- search_type 4 MV → mv/*
- top/category → top/detail

运行（Docker）: docker build -f Dockerfile.test -t qq-music-api-test . && docker run qq-music-api-test
"""

import pytest

pytest.importorskip("fastapi", reason="需要 web 依赖: uv sync --group web --group testing")

from fastapi.testclient import TestClient

from web.app import app
from web.routes_config import ROUTES

client = TestClient(app)
KEYWORD = "周杰伦"


def _check_response(response, path: str, allow_500: bool = False):
    """校验响应：非 500（除 allow_500 外），结构含 code"""
    if not allow_500:
        assert response.status_code != 500, f"{path} 返回 500: {response.text}"
    try:
        data = response.json()
    except Exception:
        if allow_500 and response.status_code == 500:
            return {}  # 500 可能是 HTML 错误页
        raise AssertionError(f"{path} 响应非 JSON: {response.text[:200]}")
    assert "code" in data or (allow_500 and response.status_code == 500)
    return data


def _first(items: list, *keys, default=None):
    """从列表中取首项，按 keys 顺序取第一个存在的字段"""
    if not items or not isinstance(items[0], dict):
        return default
    for k in keys:
        if k in items[0] and items[0][k] is not None:
            return items[0][k]
    return default


def _first_str(items: list, *keys, default=""):
    """取字符串类型，兼容多个字段名"""
    v = _first(items, *keys, default=default)
    return str(v) if v is not None else default


def _first_int(items: list, *keys, default=0):
    """取整型"""
    v = _first(items, *keys, default=default)
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


@pytest.fixture(scope="module")
def api_ids():
    """
    通过 search/top 获取真实 ID，供依赖接口使用。
    失败时使用兜底值，确保测试可运行。
    """
    ids = {
        "song_id": 212127,
        "song_mid": "003RMaRI1iFuY",
        "singer_mid": "0025NhlN2yWrP4",
        "album_id": "000a0knE3b7lP4",
        "songlist_id": 3311580048,
        "mv_vid": "m00148a0xwd",
        "top_id": 4,
        "biz_id": "212127",
    }

    # 1. 歌曲 search_type=0 → song/*, lyric, comment
    r = client.get("/search/by_type", params={"keyword": KEYWORD, "search_type": 0, "num": 5})
    if r.status_code == 200 and r.json().get("code") == 200:
        items = r.json().get("data") or []
        if items:
            ids["song_id"] = _first_int(items, "id", "songid", "song_id", default=ids["song_id"])
            ids["song_mid"] = _first_str(items, "mid", "songmid", "song_mid") or ids["song_mid"]
            ids["biz_id"] = str(ids["song_id"])

    # 2. 歌手 search_type=1 → singer/*
    r = client.get("/search/by_type", params={"keyword": KEYWORD, "search_type": 1, "num": 5})
    if r.status_code == 200 and r.json().get("code") == 200:
        items = r.json().get("data") or []
        if items:
            ids["singer_mid"] = _first_str(items, "mid", "singer_mid", "SingerMid") or ids["singer_mid"]

    # 3. 专辑 search_type=2 → album/*
    r = client.get("/search/by_type", params={"keyword": KEYWORD, "search_type": 2, "num": 5})
    if r.status_code == 200 and r.json().get("code") == 200:
        items = r.json().get("data") or []
        if items:
            ids["album_id"] = _first_str(items, "albummid", "album_mid", "albumid", "albumId") or ids["album_id"]

    # 4. 歌单 search_type=3 → songlist/*
    r = client.get("/search/by_type", params={"keyword": KEYWORD, "search_type": 3, "num": 5})
    if r.status_code == 200 and r.json().get("code") == 200:
        items = r.json().get("data") or []
        if items:
            ids["songlist_id"] = _first_int(items, "dissid", "disstid", "dirid", "id") or ids["songlist_id"]

    # 5. MV search_type=4 → mv/*
    r = client.get("/search/by_type", params={"keyword": KEYWORD, "search_type": 4, "num": 5})
    if r.status_code == 200 and r.json().get("code") == 200:
        items = r.json().get("data") or []
        if items:
            ids["mv_vid"] = _first_str(items, "vid", "Vid", "video_id") or ids["mv_vid"]

    # 6. top/category → top/detail
    r = client.get("/top/category")
    if r.status_code == 200 and r.json().get("code") == 200:
        data = r.json().get("data") or []
        for group in (data if isinstance(data, list) else []):
            if not isinstance(group, dict):
                continue
            items = group.get("list") or group.get("items") or group.get("toplist") or []
            if items:
                first = items[0] if isinstance(items[0], dict) else {}
                tid = first.get("topId") or first.get("top_id") or first.get("id")
                if tid is not None:
                    try:
                        ids["top_id"] = int(tid)
                    except (TypeError, ValueError):
                        pass
                    break

    return ids


# ==================== 无依赖接口：直接测 ====================

@pytest.mark.parametrize(
    "path,params",
    [
        ("/search/hotkey", {}),
        ("/search/complete", {"keyword": KEYWORD}),
        ("/search/general", {"keyword": KEYWORD, "page": 1}),
        ("/search/by_type", {"keyword": KEYWORD, "search_type": 0, "num": 5}),
        ("/singer/list", {"area": -100, "sex": -100, "genre": -100}),
        ("/top/category", {}),
        ("/recommend/feed", {}),
        ("/recommend/guess", {}),
        ("/recommend/songlist", {}),
        ("/recommend/newsong", {}),
    ],
)
def test_independent_routes(path: str, params: dict):
    """无依赖接口：不依赖 search 返回的 ID"""
    r = client.get(path, params=params)
    data = _check_response(r, path)
    if r.status_code == 200:
        assert data["code"] == 200
    else:
        assert r.status_code in (400, 401, 422)


# ==================== 歌曲类：依赖 search 歌曲 ID ====================

@pytest.mark.parametrize(
    "path,params_builder",
    [
        ("/song/query", lambda ids: {"ids": str(ids["song_id"])}),
        ("/song/urls", lambda ids: {"mids": ids["song_mid"]}),
        ("/song/detail", lambda ids: {"value": str(ids["song_id"])}),
        ("/song/similar", lambda ids: {"songid": ids["song_id"]}),
        ("/song/labels", lambda ids: {"songid": ids["song_id"]}),
        ("/song/related_mv", lambda ids: {"songid": ids["song_id"]}),
        ("/lyric", lambda ids: {"value": str(ids["song_id"])}),
        ("/comment/count", lambda ids: {"biz_id": ids["biz_id"]}),
        ("/comment/hot", lambda ids: {"biz_id": ids["biz_id"], "page_num": 1, "page_size": 5}),
        ("/comment/new", lambda ids: {"biz_id": ids["biz_id"], "page_num": 1, "page_size": 5}),
    ],
)
def test_song_routes(path: str, params_builder, api_ids):
    """歌曲/歌词/评论：使用 search 歌曲结果"""
    params = params_builder(api_ids)
    r = client.get(path, params=params)
    data = _check_response(r, path)
    if r.status_code == 200:
        assert data["code"] == 200
    else:
        assert r.status_code in (400, 401, 422)


# ==================== 歌手类：依赖 search 歌手 mid ====================

@pytest.mark.parametrize(
    "path,params_builder",
    [
        ("/singer/info", lambda ids: {"mid": ids["singer_mid"]}),
        ("/singer/songs", lambda ids: {"mid": ids["singer_mid"], "page": 1, "num": 10}),
        ("/singer/albums", lambda ids: {"mid": ids["singer_mid"], "page": 1, "num": 10}),
        ("/singer/desc", lambda ids: {"mids": ids["singer_mid"]}),
    ],
)
def test_singer_routes(path: str, params_builder, api_ids):
    """歌手：使用 search 歌手结果"""
    params = params_builder(api_ids)
    r = client.get(path, params=params)
    data = _check_response(r, path)
    if r.status_code == 200:
        assert data["code"] == 200
    else:
        assert r.status_code in (400, 401, 422)


# ==================== 专辑类：依赖 search 专辑 ====================

@pytest.mark.parametrize(
    "path,params_builder",
    [
        ("/album/detail", lambda ids: {"value": ids["album_id"]}),
        ("/album/songs", lambda ids: {"value": ids["album_id"], "num": 10, "page": 1}),
        ("/album/cover", lambda ids: {"mid": ids["album_id"], "size": 300}),
    ],
)
def test_album_routes(path: str, params_builder, api_ids):
    """专辑：使用 search 专辑结果"""
    params = params_builder(api_ids)
    r = client.get(path, params=params)
    data = _check_response(r, path)
    if r.status_code == 200:
        assert data["code"] == 200
    else:
        assert r.status_code in (400, 401, 422)


# ==================== 歌单类：依赖 search 歌单 ====================

@pytest.mark.parametrize(
    "path,params_builder",
    [
        ("/songlist/detail", lambda ids: {"songlist_id": ids["songlist_id"], "num": 10, "page": 1}),
        ("/songlist/songs", lambda ids: {"songlist_id": ids["songlist_id"]}),
    ],
)
def test_songlist_routes(path: str, params_builder, api_ids):
    """歌单：使用 search 歌单结果"""
    params = params_builder(api_ids)
    r = client.get(path, params=params)
    data = _check_response(r, path)
    if r.status_code == 200:
        assert data["code"] == 200
    else:
        assert r.status_code in (400, 401, 422)


# ==================== 排行榜：依赖 top/category ====================

def test_top_detail(api_ids):
    """排行榜详情：使用 top/category 的 top_id"""
    r = client.get("/top/detail", params={"top_id": api_ids["top_id"], "num": 10, "page": 1})
    data = _check_response(r, "/top/detail")
    if r.status_code == 200:
        assert data["code"] == 200
    else:
        assert r.status_code in (400, 401, 422)


# ==================== MV 类：依赖 search MV ====================

@pytest.mark.parametrize(
    "path,params_builder",
    [
        ("/mv/detail", lambda ids: {"vids": ids["mv_vid"]}),
        ("/mv/urls", lambda ids: {"vids": ids["mv_vid"]}),
    ],
)
def test_mv_routes(path: str, params_builder, api_ids):
    """MV：使用 search MV 结果"""
    params = params_builder(api_ids)
    r = client.get(path, params=params)
    data = _check_response(r, path)
    if r.status_code == 200:
        assert data["code"] == 200
    else:
        assert r.status_code in (400, 401, 422)


# ==================== 用户类：需 euin，无 search 来源，用占位 ====================

@pytest.mark.parametrize(
    "path,params",
    [
        ("/user/homepage", {"euin": "o0w_bie5hbp2h"}),
        ("/user/vip", {}),
        ("/user/follow_singers", {"euin": "o0w_bie5hbp2h", "page": 1, "num": 10}),
        ("/user/fans", {"euin": "o0w_bie5hbp2h", "page": 1, "num": 10}),
        ("/user/friends", {"page": 1, "num": 10}),
        ("/user/fav_songs", {"euin": "o0w_bie5hbp2h", "page": 1, "num": 10}),
        ("/user/fav_songlists", {"euin": "o0w_bie5hbp2h", "page": 1, "num": 10}),
    ],
)
def test_user_routes(path: str, params: dict):
    """用户：需 cookie/euin，仅校验端点可达、无连接级错误"""
    r = client.get(path, params=params)
    _check_response(r, path, allow_500=True)


# ==================== 文档与泛化路由 ====================

def test_openapi_docs_available():
    assert client.get("/docs").status_code == 200


def test_openapi_schema_available():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema and "/search/hotkey" in schema["paths"]


def test_generic_route():
    """泛化路由 /{module}/{func}"""
    r = client.get("/top/get_top_category")
    data = _check_response(r, "/top/get_top_category")
    assert r.status_code == 200 and data["code"] == 200


def test_api_response_structure():
    r = client.get("/search/hotkey")
    assert r.status_code == 200
    data = r.json()
    assert "code" in data and "message" in data and "timestamp" in data
    assert data["code"] == 200


# ==================== 覆盖检查：确保所有 ROUTES 都被测到 ====================

def test_all_routes_covered(api_ids):
    """确保 routes_config 中所有路由均有对应测试"""
    covered = {
        "/search/hotkey", "/search/complete", "/search/general", "/search/by_type",
        "/song/query", "/song/urls", "/song/detail", "/song/similar", "/song/labels", "/song/related_mv",
        "/singer/list", "/singer/info", "/singer/songs", "/singer/albums", "/singer/desc",
        "/album/detail", "/album/songs", "/album/cover",
        "/songlist/detail", "/songlist/songs",
        "/top/category", "/top/detail",
        "/mv/detail", "/mv/urls",
        "/lyric", "/comment/count", "/comment/hot", "/comment/new",
        "/recommend/feed", "/recommend/guess", "/recommend/songlist", "/recommend/newsong",
        "/user/homepage", "/user/vip", "/user/follow_singers", "/user/fans", "/user/friends",
        "/user/fav_songs", "/user/fav_songlists",
    }
    configured = {r["path"] for r in ROUTES}
    assert configured <= covered, f"未覆盖的路由: {configured - covered}"
