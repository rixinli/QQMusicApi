"""
路由配置 - 方案 C：配置驱动的路由注册
单点维护路径、模块、函数及 Swagger 元信息，兼顾代码量与可维护性。
格式: (path, tags, summary, module, func)
  - module/func 为 None 时使用 handler 名
  - 路径与底层函数名可映射（如 /search/general -> general_search）
"""

from typing import TypedDict


class RouteSpec(TypedDict, total=False):
    path: str
    tags: str
    summary: str
    module: str
    func: str
    handler: str  # 自定义 handler 名，用于需特殊逻辑的接口


# 标准路由：module + func 直接映射，使用 Parser 解析
# 自定义路由：handler 指定，在 handlers.py 中实现
ROUTES: list[RouteSpec] = [
    # ==================== 搜索 ====================
    {"path": "/search/hotkey", "tags": "搜索", "summary": "获取热搜词", "module": "search", "func": "hotkey"},
    {"path": "/search/complete", "tags": "搜索", "summary": "搜索词补全", "handler": "search_complete"},
    {"path": "/search/general", "tags": "搜索", "summary": "综合搜索", "handler": "search_general"},
    {"path": "/search/by_type", "tags": "搜索", "summary": "按类型搜索", "handler": "search_by_type"},
    # ==================== 歌曲 ====================
    {"path": "/song/query", "tags": "歌曲", "summary": "获取歌曲信息", "handler": "song_query"},
    {"path": "/song/urls", "tags": "歌曲", "summary": "获取歌曲播放链接", "handler": "song_urls"},
    {"path": "/song/detail", "tags": "歌曲", "summary": "获取歌曲详情", "handler": "song_detail"},
    {"path": "/song/similar", "tags": "歌曲", "summary": "获取相似歌曲", "handler": "song_similar"},
    {"path": "/song/labels", "tags": "歌曲", "summary": "获取歌曲标签", "handler": "song_labels"},
    {"path": "/song/related_mv", "tags": "歌曲", "summary": "获取相关MV", "handler": "song_related_mv"},
    # ==================== 歌手 ====================
    {"path": "/singer/list", "tags": "歌手", "summary": "获取歌手列表", "handler": "singer_list"},
    {"path": "/singer/info", "tags": "歌手", "summary": "获取歌手信息", "handler": "singer_info"},
    {"path": "/singer/songs", "tags": "歌手", "summary": "获取歌手歌曲", "handler": "singer_songs"},
    {"path": "/singer/albums", "tags": "歌手", "summary": "获取歌手专辑", "handler": "singer_albums"},
    {"path": "/singer/desc", "tags": "歌手", "summary": "获取歌手简介", "handler": "singer_desc"},
    # ==================== 专辑 ====================
    {"path": "/album/detail", "tags": "专辑", "summary": "获取专辑详情", "handler": "album_detail"},
    {"path": "/album/songs", "tags": "专辑", "summary": "获取专辑歌曲", "handler": "album_songs"},
    {"path": "/album/cover", "tags": "专辑", "summary": "获取专辑封面", "handler": "album_cover"},
    # ==================== 歌单 ====================
    {"path": "/songlist/detail", "tags": "歌单", "summary": "获取歌单详情", "handler": "songlist_detail"},
    {"path": "/songlist/songs", "tags": "歌单", "summary": "获取歌单所有歌曲", "handler": "songlist_songs"},
    # ==================== 排行榜 ====================
    {"path": "/top/category", "tags": "排行榜", "summary": "获取排行榜分类", "module": "top", "func": "get_top_category"},
    {"path": "/top/detail", "tags": "排行榜", "summary": "获取排行榜详情", "handler": "top_detail"},
    # ==================== MV ====================
    {"path": "/mv/detail", "tags": "MV", "summary": "获取MV详情", "handler": "mv_detail"},
    {"path": "/mv/urls", "tags": "MV", "summary": "获取MV播放链接", "handler": "mv_urls"},
    # ==================== 歌词 ====================
    {"path": "/lyric", "tags": "歌词", "summary": "获取歌词", "handler": "lyric"},
    # ==================== 评论 ====================
    {"path": "/comment/count", "tags": "评论", "summary": "获取评论数量", "handler": "comment_count"},
    {"path": "/comment/hot", "tags": "评论", "summary": "获取热评", "handler": "comment_hot"},
    {"path": "/comment/new", "tags": "评论", "summary": "获取最新评论", "handler": "comment_new"},
    # ==================== 推荐 ====================
    {"path": "/recommend/feed", "tags": "推荐", "summary": "获取主页推荐", "handler": "recommend_feed"},
    {"path": "/recommend/guess", "tags": "推荐", "summary": "猜你喜欢", "handler": "recommend_guess"},
    {"path": "/recommend/songlist", "tags": "推荐", "summary": "推荐歌单", "handler": "recommend_songlist"},
    {"path": "/recommend/newsong", "tags": "推荐", "summary": "推荐新歌", "handler": "recommend_newsong"},
    # ==================== 用户 ====================
    {"path": "/user/homepage", "tags": "用户", "summary": "获取用户主页", "handler": "user_homepage"},
    {"path": "/user/vip", "tags": "用户", "summary": "获取VIP信息", "handler": "user_vip"},
    {"path": "/user/follow_singers", "tags": "用户", "summary": "获取关注歌手", "handler": "user_follow_singers"},
    {"path": "/user/fans", "tags": "用户", "summary": "获取粉丝列表", "handler": "user_fans"},
    {"path": "/user/friends", "tags": "用户", "summary": "获取好友列表", "handler": "user_friends"},
    {"path": "/user/fav_songs", "tags": "用户", "summary": "获取收藏歌曲", "handler": "user_fav_songs"},
    {"path": "/user/fav_songlists", "tags": "用户", "summary": "获取收藏歌单", "handler": "user_fav_songlists"},
]
