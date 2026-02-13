"""WEB API Port (完整优化版)"""

from enum import Enum
from time import time
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

from qqmusic_api import album, comment, lyric, mv, search, singer, song, songlist, top, user
import qqmusic_api
from qqmusic_api.recommend import get_guess_recommend, get_home_feed, get_recommend_newsong, get_recommend_songlist
from qqmusic_api.utils.credential import Credential
from web.parser import Parser


class ApiResponseModel(BaseModel):
    """API响应数据模型"""

    code: int
    message: str
    data: Any = None
    errors: list[str] | None = None
    timestamp: int


class ApiResponse(ORJSONResponse):
    """标准化API响应类"""

    def __init__(
        self,
        status_code: int = status.HTTP_200_OK,
        message: str = "Success",
        data: Any = None,
        errors: str | list[str] | None = None,
        **kwargs,
    ):
        processed_errors = None
        if errors:
            processed_errors = [errors] if isinstance(errors, str) else errors

        content = ApiResponseModel(
            code=status_code, message=message, data=data, errors=processed_errors, timestamp=int(time())
        ).dict(exclude_unset=True, exclude_defaults=True)

        super().__init__(content=content, status_code=status_code, **kwargs)

    @classmethod
    def success(
        cls, data: Any = None, message: str = "Success", status_code: int = status.HTTP_200_OK
    ) -> "ApiResponse":
        """构建成功响应"""
        return cls(status_code=status_code, message=message, data=data)

    @classmethod
    def error(
        cls, errors: str | list[str], message: str = "Error", status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> "ApiResponse":
        """构建错误响应"""
        return cls(status_code=status_code, message=message, errors=errors)


app = FastAPI(
    title="QQMusic API",
    description="QQMusic API Web Port - 支持 Swagger 测试",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ApiResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(404)
async def _not_found_handler(request: Request, exc: HTTPException):
    return ApiResponse.error(errors="请求的资源不存在", message="Not Found", status_code=status.HTTP_404_NOT_FOUND)


@app.exception_handler(500)
async def _server_error_handler(request: Request, exc: HTTPException):
    return ApiResponse.error(
        errors=["服务器内部错误"], message="Internal Server Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@app.exception_handler(422)
async def _validation_error_handler(request: Request, exc: HTTPException):
    return ApiResponse.error(
        errors=["参数验证失败"], message="Validation Error", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


def get_credential(request: Request):
    """获取凭证"""
    try:
        credential = qqmusic_api.Credential.from_cookies_dict(request.cookies)
        qqmusic_api.get_session().credential = credential
        return credential
    except Exception:
        return None


async def _api_web(
    request: Request,
    module: str,
    func: str,
):
    """统一API请求处理"""
    try:
        credential = qqmusic_api.Credential.from_cookies_dict(request.cookies)
        qqmusic_api.get_session().credential = credential
    except Exception:
        return ApiResponse.error(
            errors="无效的用户凭证", message="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED
        )

    params = dict(request.query_params)
    parser = Parser(module, func, params)

    try:
        result, errors = await parser.parse()
    except Exception:
        return ApiResponse.error(
            errors=["服务器处理请求时发生异常"],
            message="Internal Error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if errors:
        return ApiResponse.error(
            errors=errors, message="Request Validation Failed", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    if not parser.valid:
        return ApiResponse.error(
            errors=["无效的请求参数"], message="Bad Request", status_code=status.HTTP_400_BAD_REQUEST
        )

    return ApiResponse.success(data=result, message="请求成功")


app.add_api_route(
    path="/{module}/{func}",
    endpoint=_api_web,
    methods=["GET"],
    responses={
        200: {"model": ApiResponseModel},
        400: {"model": ApiResponseModel},
        401: {"model": ApiResponseModel},
        422: {"model": ApiResponseModel},
        500: {"model": ApiResponseModel},
    },
)


# ==================== 搜索模块 ====================
class SearchTypeEnum(str, Enum):
    SONG = "SONG"
    SINGER = "SINGER"
    ALBUM = "ALBUM"
    SONGLIST = "SONGLIST"
    MV = "MV"
    LYRIC = "LYRIC"
    USER = "USER"


@app.get("/search/hotkey", tags=["搜索"], summary="获取热搜词")
async def search_hotkey():
    """获取热搜词"""
    result = await qqmusic_api.search.hotkey()
    return ApiResponse.success(data=result)


@app.get("/search/complete", tags=["搜索"], summary="搜索词补全")
async def search_complete(keyword: str = Query(..., description="关键词")):
    """搜索词补全"""
    result = await qqmusic_api.search.complete(keyword=keyword)
    return ApiResponse.success(data=result)


@app.get("/search/general", tags=["搜索"], summary="综合搜索")
async def search_general(
    keyword: str = Query(..., description="关键词"),
    page: int = Query(1, description="页码"),
    highlight: bool = Query(True, description="是否高亮"),
):
    """综合搜索"""
    result = await qqmusic_api.search.general_search(keyword=keyword, page=page, highlight=highlight)
    return ApiResponse.success(data=result)


@app.get("/search/by_type", tags=["搜索"], summary="按类型搜索")
async def search_by_type(
    keyword: str = Query(..., description="关键词"),
    search_type: int = Query(0, description="搜索类型: 0=歌曲, 1=歌手, 2=专辑, 3=歌单, 4=MV, 7=歌词, 8=用户"),
    num: int = Query(10, description="返回数量"),
    page: int = Query(1, description="页码"),
    highlight: bool = Query(True, description="是否高亮"),
):
    """按类型搜索"""
    from qqmusic_api.search import SearchType
    result = await qqmusic_api.search.search_by_type(
        keyword=keyword, search_type=SearchType(search_type), num=num, page=page, highlight=highlight
    )
    return ApiResponse.success(data=result)


# ==================== 歌曲模块 ====================
@app.get("/song/query", tags=["歌曲"], summary="获取歌曲信息")
async def song_query(
    ids: str = Query(..., description="歌曲ID列表，逗号分隔"),
):
    """根据ID获取歌曲信息"""
    id_list = [int(x) for x in ids.split(",")]
    result = await qqmusic_api.song.query_song(id_list)
    return ApiResponse.success(data=result)


@app.get("/song/urls", tags=["歌曲"], summary="获取歌曲播放链接")
async def song_urls(
    mids: str = Query(..., description="歌曲mid列表，逗号分隔"),
    file_type: str = Query("MP3_128", description="文件类型: MP3_128, MP3_320, FLAC, OGG_320等"),
    request: Request = None,
):
    """获取歌曲播放链接"""
    mid_list = mids.split(",")
    from qqmusic_api.song import SongFileType
    try:
        ft = SongFileType[file_type]
    except KeyError:
        ft = SongFileType.MP3_128
    credential = get_credential(request) if request else None
    result = await qqmusic_api.song.get_song_urls(mid_list, ft, credential=credential)
    return ApiResponse.success(data=result)


@app.get("/song/detail", tags=["歌曲"], summary="获取歌曲详情")
async def song_detail(
    value: str = Query(..., description="歌曲ID或mid"),
):
    """获取歌曲详细信息"""
    try:
        song_id = int(value)
        result = await qqmusic_api.song.get_detail(song_id)
    except ValueError:
        result = await qqmusic_api.song.get_detail(value)
    return ApiResponse.success(data=result)


@app.get("/song/similar", tags=["歌曲"], summary="获取相似歌曲")
async def song_similar(
    songid: int = Query(..., description="歌曲ID"),
):
    """获取相似歌曲"""
    result = await qqmusic_api.song.get_similar_song(songid)
    return ApiResponse.success(data=result)


@app.get("/song/labels", tags=["歌曲"], summary="获取歌曲标签")
async def song_labels(
    songid: int = Query(..., description="歌曲ID"),
):
    """获取歌曲标签"""
    result = await qqmusic_api.song.get_lables(songid)
    return ApiResponse.success(data=result)


@app.get("/song/related_mv", tags=["歌曲"], summary="获取相关MV")
async def song_related_mv(
    songid: int = Query(..., description="歌曲ID"),
):
    """获取相关MV"""
    result = await qqmusic_api.song.get_related_mv(songid)
    return ApiResponse.success(data=result)


# ==================== 歌手模块 ====================
class AreaTypeEnum(int, Enum):
    ALL = -100
    CHINA = 200
    TAIWAN = 2
    AMERICA = 5
    JAPAN = 4
    KOREA = 3


class SexTypeEnum(int, Enum):
    ALL = -100
    MALE = 0
    FEMALE = 1
    GROUP = 2


@app.get("/singer/list", tags=["歌手"], summary="获取歌手列表")
async def singer_list(
    area: int = Query(-100, description="地区: -100=全部, 200=内地, 2=港台, 5=欧美, 4=日本, 3=韩国"),
    sex: int = Query(-100, description="性别: -100=全部, 0=男, 1=女, 2=乐队"),
    genre: int = Query(-100, description="风格: -100=全部, 7=流行, 3=说唱, 19=国风, 4=摇滚, 2=电子"),
):
    """获取歌手列表"""
    from qqmusic_api.singer import AreaType, GenreType, SexType
    result = await qqmusic_api.singer.get_singer_list(
        area=AreaType(area), sex=SexType(sex), genre=GenreType(genre)
    )
    return ApiResponse.success(data=result)


@app.get("/singer/info", tags=["歌手"], summary="获取歌手信息")
async def singer_info(
    mid: str = Query(..., description="歌手mid"),
):
    """获取歌手基本信息"""
    result = await qqmusic_api.singer.get_info(mid)
    return ApiResponse.success(data=result)


@app.get("/singer/songs", tags=["歌手"], summary="获取歌手歌曲")
async def singer_songs(
    mid: str = Query(..., description="歌手mid"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="返回数量"),
):
    """获取歌手歌曲"""
    from qqmusic_api.singer import TabType
    result = await qqmusic_api.singer.get_tab_detail(mid, TabType.SONG, page, num)
    return ApiResponse.success(data=result)


@app.get("/singer/albums", tags=["歌手"], summary="获取歌手专辑")
async def singer_albums(
    mid: str = Query(..., description="歌手mid"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="返回数量"),
):
    """获取歌手专辑"""
    from qqmusic_api.singer import TabType
    result = await qqmusic_api.singer.get_tab_detail(mid, TabType.ALBUM, page, num)
    return ApiResponse.success(data=result)


@app.get("/singer/desc", tags=["歌手"], summary="获取歌手简介")
async def singer_desc(
    mids: str = Query(..., description="歌手mid列表，逗号分隔"),
):
    """获取歌手简介"""
    mid_list = mids.split(",")
    result = await qqmusic_api.singer.get_desc(mid_list)
    return ApiResponse.success(data=result)


# ==================== 专辑模块 ====================
@app.get("/album/detail", tags=["专辑"], summary="获取专辑详情")
async def album_detail(
    value: str = Query(..., description="专辑ID或mid"),
):
    """获取专辑详细信息"""
    try:
        album_id = int(value)
        result = await qqmusic_api.album.get_detail(album_id)
    except ValueError:
        result = await qqmusic_api.album.get_detail(value)
    return ApiResponse.success(data=result)


@app.get("/album/songs", tags=["专辑"], summary="获取专辑歌曲")
async def album_songs(
    value: str = Query(..., description="专辑ID或mid"),
    num: int = Query(10, description="返回数量"),
    page: int = Query(1, description="页码"),
):
    """获取专辑歌曲"""
    try:
        album_id = int(value)
        result = await qqmusic_api.album.get_song(album_id, num, page)
    except ValueError:
        result = await qqmusic_api.album.get_song(value, num, page)
    return ApiResponse.success(data=result)


@app.get("/album/cover", tags=["专辑"], summary="获取专辑封面")
async def album_cover(
    mid: str = Query(..., description="专辑mid"),
    size: int = Query(300, description="封面大小: 150, 300, 500, 800"),
):
    """获取专辑封面链接"""
    result = qqmusic_api.album.get_cover(mid, size)
    return ApiResponse.success(data=result)


# ==================== 歌单模块 ====================
@app.get("/songlist/detail", tags=["歌单"], summary="获取歌单详情")
async def songlist_detail(
    songlist_id: int = Query(..., description="歌单ID"),
    num: int = Query(10, description="返回数量"),
    page: int = Query(1, description="页码"),
    onlysong: bool = Query(False, description="仅返回歌曲"),
):
    """获取歌单详情"""
    result = await qqmusic_api.songlist.get_detail(songlist_id, num=num, page=page, onlysong=onlysong)
    return ApiResponse.success(data=result)


@app.get("/songlist/songs", tags=["歌单"], summary="获取歌单所有歌曲")
async def songlist_songs(
    songlist_id: int = Query(..., description="歌单ID"),
):
    """获取歌单所有歌曲"""
    result = await qqmusic_api.songlist.get_songlist(songlist_id)
    return ApiResponse.success(data=result)


# ==================== 排行榜模块 ====================
@app.get("/top/category", tags=["排行榜"], summary="获取排行榜分类")
async def top_category():
    """获取所有排行榜"""
    result = await qqmusic_api.top.get_top_category()
    return ApiResponse.success(data=result)


@app.get("/top/detail", tags=["排行榜"], summary="获取排行榜详情")
async def top_detail(
    top_id: int = Query(..., description="排行榜ID"),
    num: int = Query(10, description="返回数量"),
    page: int = Query(1, description="页码"),
):
    """获取排行榜详情"""
    result = await qqmusic_api.top.get_detail(top_id, num, page)
    return ApiResponse.success(data=result)


# ==================== MV模块 ====================
@app.get("/mv/detail", tags=["MV"], summary="获取MV详情")
async def mv_detail(
    vids: str = Query(..., description="视频vid列表，逗号分隔"),
):
    """获取MV详细信息"""
    vid_list = vids.split(",")
    result = await qqmusic_api.mv.get_detail(vid_list)
    return ApiResponse.success(data=result)


@app.get("/mv/urls", tags=["MV"], summary="获取MV播放链接")
async def mv_urls(
    vids: str = Query(..., description="视频vid列表，逗号分隔"),
):
    """获取MV播放链接"""
    vid_list = vids.split(",")
    result = await qqmusic_api.mv.get_mv_urls(vid_list)
    return ApiResponse.success(data=result)


# ==================== 歌词模块 ====================
@app.get("/lyric", tags=["歌词"], summary="获取歌词")
async def lyric(
    value: str = Query(..., description="歌曲ID或mid"),
    qrc: bool = Query(False, description="逐字歌词"),
    trans: bool = Query(False, description="翻译歌词"),
    roma: bool = Query(False, description="罗马歌词"),
):
    """获取歌词"""
    try:
        song_id = int(value)
        result = await qqmusic_api.lyric.get_lyric(song_id, qrc, trans, roma)
    except ValueError:
        result = await qqmusic_api.lyric.get_lyric(value, qrc, trans, roma)
    return ApiResponse.success(data=result)


# ==================== 评论模块 ====================
@app.get("/comment/count", tags=["评论"], summary="获取评论数量")
async def comment_count(
    biz_id: str = Query(..., description="歌曲ID"),
):
    """获取评论数量"""
    result = await qqmusic_api.comment.get_comment_count(biz_id)
    return ApiResponse.success(data=result)


@app.get("/comment/hot", tags=["评论"], summary="获取热评")
async def comment_hot(
    biz_id: str = Query(..., description="歌曲ID"),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(15, description="每页数量"),
):
    """获取热评"""
    result = await qqmusic_api.comment.get_hot_comments(biz_id, page_num, page_size)
    return ApiResponse.success(data=result)


@app.get("/comment/new", tags=["评论"], summary="获取最新评论")
async def comment_new(
    biz_id: str = Query(..., description="歌曲ID"),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(15, description="每页数量"),
):
    """获取最新评论"""
    result = await qqmusic_api.comment.get_new_comments(biz_id, page_num, page_size)
    return ApiResponse.success(data=result)


# ==================== 推荐模块 ====================
@app.get("/recommend/feed", tags=["推荐"], summary="获取主页推荐")
async def recommend_feed():
    """获取主页推荐"""
    result = await get_home_feed()
    return ApiResponse.success(data=result)


@app.get("/recommend/guess", tags=["推荐"], summary="猜你喜欢")
async def recommend_guess():
    """获取猜你喜欢"""
    result = await get_guess_recommend()
    return ApiResponse.success(data=result)


@app.get("/recommend/songlist", tags=["推荐"], summary="推荐歌单")
async def recommend_songlist():
    """获取推荐歌单"""
    result = await get_recommend_songlist()
    return ApiResponse.success(data=result)


@app.get("/recommend/newsong", tags=["推荐"], summary="推荐新歌")
async def recommend_newsong():
    """获取推荐新歌"""
    result = await get_recommend_newsong()
    return ApiResponse.success(data=result)


# ==================== 用户模块 ====================
@app.get("/user/homepage", tags=["用户"], summary="获取用户主页")
async def user_homepage(
    euin: str = Query(..., description="encrypt_uin"),
    request: Request = None,
):
    """获取用户主页"""
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_homepage(euin, credential=credential)
    return ApiResponse.success(data=result)


@app.get("/user/vip", tags=["用户"], summary="获取VIP信息")
async def user_vip(request: Request = None):
    """获取VIP信息"""
    credential = get_credential(request)
    if not credential:
        return ApiResponse.error(errors="需要登录", status_code=status.HTTP_401_UNAUTHORIZED)
    result = await qqmusic_api.user.get_vip_info(credential=credential)
    return ApiResponse.success(data=result)


@app.get("/user/follow_singers", tags=["用户"], summary="获取关注歌手")
async def user_follow_singers(
    euin: str = Query(..., description="encrypt_uin"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    """获取关注歌手"""
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_follow_singers(euin, page, num, credential=credential)
    return ApiResponse.success(data=result)


@app.get("/user/fans", tags=["用户"], summary="获取粉丝列表")
async def user_fans(
    euin: str = Query(..., description="encrypt_uin"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    """获取粉丝列表"""
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_fans(euin, page, num, credential=credential)
    return ApiResponse.success(data=result)


@app.get("/user/friends", tags=["用户"], summary="获取好友列表")
async def user_friends(
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    """获取好友列表"""
    credential = get_credential(request)
    if not credential:
        return ApiResponse.error(errors="需要登录", status_code=status.HTTP_401_UNAUTHORIZED)
    result = await qqmusic_api.user.get_friend(page, num, credential=credential)
    return ApiResponse.success(data=result)


@app.get("/user/fav_songs", tags=["用户"], summary="获取收藏歌曲")
async def user_fav_songs(
    euin: str = Query(..., description="encrypt_uin"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    """获取收藏歌曲"""
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_fav_song(euin, page, num, credential=credential)
    return ApiResponse.success(data=result)


@app.get("/user/fav_songlists", tags=["用户"], summary="获取收藏歌单")
async def user_fav_songlists(
    euin: str = Query(..., description="encrypt_uin"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    """获取收藏歌单"""
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_fav_songlist(euin, page, num, credential=credential)
    return ApiResponse.success(data=result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug",
    )
