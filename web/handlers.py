"""
自定义 Handlers - 需参数映射、枚举转换或凭证校验的接口
"""

from fastapi import Query, Request, status

import qqmusic_api
from qqmusic_api.recommend import (
    get_guess_recommend,
    get_home_feed,
    get_recommend_newsong,
    get_recommend_songlist,
)
from qqmusic_api.search import SearchType

from web.common import ApiResponse, get_credential


async def search_general(
    keyword: str = Query(..., description="关键词"),
    page: int = Query(1, description="页码"),
    highlight: bool = Query(True, description="是否高亮"),
):
    result = await qqmusic_api.search.general_search(keyword=keyword, page=page, highlight=highlight)
    return ApiResponse.success(data=result)


async def search_complete(keyword: str = Query(..., description="关键词")):
    result = await qqmusic_api.search.complete(keyword=keyword)
    return ApiResponse.success(data=result)


async def search_by_type(
    keyword: str = Query(..., description="关键词"),
    search_type: int = Query(0, description="0=歌曲,1=歌手,2=专辑,3=歌单,4=MV,7=歌词,8=用户"),
    num: int = Query(10, description="返回数量"),
    page: int = Query(1, description="页码"),
    highlight: bool = Query(True, description="是否高亮"),
):
    result = await qqmusic_api.search.search_by_type(
        keyword=keyword, search_type=SearchType(search_type), num=num, page=page, highlight=highlight
    )
    return ApiResponse.success(data=result)


async def song_query(ids: str = Query(..., description="歌曲ID列表，逗号分隔")):
    id_list = [int(x) for x in ids.split(",")]
    result = await qqmusic_api.song.query_song(id_list)
    return ApiResponse.success(data=result)


async def song_urls(
    mids: str = Query(..., description="歌曲mid列表，逗号分隔"),
    file_type: str = Query("MP3_128", description="MP3_128, MP3_320, FLAC, OGG_320等"),
    request: Request = None,
):
    mid_list = mids.split(",")
    from qqmusic_api.song import SongFileType
    try:
        ft = SongFileType[file_type]
    except KeyError:
        ft = SongFileType.MP3_128
    credential = get_credential(request) if request else None
    result = await qqmusic_api.song.get_song_urls(mid_list, ft, credential=credential)
    return ApiResponse.success(data=result)


async def song_detail(value: str = Query(..., description="歌曲ID或mid")):
    try:
        song_id = int(value)
        result = await qqmusic_api.song.get_detail(song_id)
    except ValueError:
        result = await qqmusic_api.song.get_detail(value)
    return ApiResponse.success(data=result)


async def song_similar(songid: int = Query(..., description="歌曲ID")):
    result = await qqmusic_api.song.get_similar_song(songid)
    return ApiResponse.success(data=result)


async def song_labels(songid: int = Query(..., description="歌曲ID")):
    result = await qqmusic_api.song.get_lables(songid)
    return ApiResponse.success(data=result)


async def song_related_mv(
    songid: int = Query(..., description="歌曲ID"),
    last_mvid: str = Query("", description="上一页最后一条MV的id"),
):
    result = await qqmusic_api.song.get_related_mv(songid, last_mvid or None)
    return ApiResponse.success(data=result)


async def singer_info(mid: str = Query(..., description="歌手mid")):
    result = await qqmusic_api.singer.get_info(mid)
    return ApiResponse.success(data=result)


async def singer_desc(mids: str = Query(..., description="歌手mid列表，逗号分隔")):
    mid_list = mids.split(",")
    result = await qqmusic_api.singer.get_desc(mid_list)
    return ApiResponse.success(data=result)


async def album_cover(
    mid: str = Query(..., description="专辑mid"),
    size: int = Query(300, description="封面大小: 150, 300, 500, 800"),
):
    result = qqmusic_api.album.get_cover(mid, size)
    return ApiResponse.success(data=result)


async def songlist_detail(
    songlist_id: int = Query(..., description="歌单ID"),
    num: int = Query(10, description="返回数量"),
    page: int = Query(1, description="页码"),
    onlysong: bool = Query(False, description="仅返回歌曲"),
):
    result = await qqmusic_api.songlist.get_detail(songlist_id, num=num, page=page, onlysong=onlysong)
    return ApiResponse.success(data=result)


async def songlist_songs(songlist_id: int = Query(..., description="歌单ID")):
    result = await qqmusic_api.songlist.get_songlist(songlist_id)
    return ApiResponse.success(data=result)


async def top_detail(
    top_id: int = Query(..., description="排行榜ID"),
    num: int = Query(10, description="返回数量"),
    page: int = Query(1, description="页码"),
):
    result = await qqmusic_api.top.get_detail(top_id, num, page)
    return ApiResponse.success(data=result)


async def mv_detail(vids: str = Query(..., description="视频vid列表，逗号分隔")):
    vid_list = vids.split(",")
    result = await qqmusic_api.mv.get_detail(vid_list)
    return ApiResponse.success(data=result)


async def mv_urls(vids: str = Query(..., description="视频vid列表，逗号分隔")):
    vid_list = vids.split(",")
    result = await qqmusic_api.mv.get_mv_urls(vid_list)
    return ApiResponse.success(data=result)


async def comment_count(biz_id: str = Query(..., description="歌曲ID")):
    result = await qqmusic_api.comment.get_comment_count(biz_id)
    return ApiResponse.success(data=result)


async def comment_hot(
    biz_id: str = Query(..., description="歌曲ID"),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(15, description="每页数量"),
):
    result = await qqmusic_api.comment.get_hot_comments(biz_id, page_num, page_size)
    return ApiResponse.success(data=result)


async def comment_new(
    biz_id: str = Query(..., description="歌曲ID"),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(15, description="每页数量"),
):
    result = await qqmusic_api.comment.get_new_comments(biz_id, page_num, page_size)
    return ApiResponse.success(data=result)


async def singer_list(
    area: int = Query(-100, description="地区: -100=全部,200=内地,2=港台,5=欧美,4=日本,3=韩国"),
    sex: int = Query(-100, description="性别: -100=全部,0=男,1=女,2=乐队"),
    genre: int = Query(-100, description="风格: -100=全部,7=流行,3=说唱,19=国风等"),
):
    from qqmusic_api.singer import AreaType, GenreType, SexType
    result = await qqmusic_api.singer.get_singer_list(
        area=AreaType(area), sex=SexType(sex), genre=GenreType(genre)
    )
    return ApiResponse.success(data=result)


async def singer_songs(
    mid: str = Query(..., description="歌手mid"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="返回数量"),
):
    from qqmusic_api.singer import TabType
    result = await qqmusic_api.singer.get_tab_detail(mid, TabType.SONG, page, num)
    return ApiResponse.success(data=result)


async def singer_albums(
    mid: str = Query(..., description="歌手mid"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="返回数量"),
):
    from qqmusic_api.singer import TabType
    result = await qqmusic_api.singer.get_tab_detail(mid, TabType.ALBUM, page, num)
    return ApiResponse.success(data=result)


async def album_detail(value: str = Query(..., description="专辑ID或mid")):
    try:
        album_id = int(value)
        result = await qqmusic_api.album.get_detail(album_id)
    except ValueError:
        result = await qqmusic_api.album.get_detail(value)
    return ApiResponse.success(data=result)


async def album_songs(
    value: str = Query(..., description="专辑ID或mid"),
    num: int = Query(10, description="返回数量"),
    page: int = Query(1, description="页码"),
):
    try:
        album_id = int(value)
        result = await qqmusic_api.album.get_song(album_id, num, page)
    except ValueError:
        result = await qqmusic_api.album.get_song(value, num, page)
    return ApiResponse.success(data=result)


async def lyric(
    value: str = Query(..., description="歌曲ID或mid"),
    qrc: bool = Query(False, description="逐字歌词"),
    trans: bool = Query(False, description="翻译歌词"),
    roma: bool = Query(False, description="罗马歌词"),
):
    try:
        song_id = int(value)
        result = await qqmusic_api.lyric.get_lyric(song_id, qrc, trans, roma)
    except ValueError:
        result = await qqmusic_api.lyric.get_lyric(value, qrc, trans, roma)
    return ApiResponse.success(data=result)


async def recommend_feed():
    result = await get_home_feed()
    return ApiResponse.success(data=result)


async def recommend_guess():
    result = await get_guess_recommend()
    return ApiResponse.success(data=result)


async def recommend_songlist():
    result = await get_recommend_songlist()
    return ApiResponse.success(data=result)


async def recommend_newsong():
    result = await get_recommend_newsong()
    return ApiResponse.success(data=result)


async def user_homepage(
    euin: str = Query(..., description="encrypt_uin"),
    request: Request = None,
):
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_homepage(euin, credential=credential)
    return ApiResponse.success(data=result)


async def user_vip(request: Request = None):
    credential = get_credential(request)
    if not credential:
        return ApiResponse.error(errors="需要登录", message="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    result = await qqmusic_api.user.get_vip_info(credential=credential)
    return ApiResponse.success(data=result)


async def user_follow_singers(
    euin: str = Query(..., description="encrypt_uin"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_follow_singers(euin, page, num, credential=credential)
    return ApiResponse.success(data=result)


async def user_fans(
    euin: str = Query(..., description="encrypt_uin"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_fans(euin, page, num, credential=credential)
    return ApiResponse.success(data=result)


async def user_friends(
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    credential = get_credential(request)
    if not credential:
        return ApiResponse.error(errors="需要登录", message="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    result = await qqmusic_api.user.get_friend(page, num, credential=credential)
    return ApiResponse.success(data=result)


async def user_fav_songs(
    euin: str = Query(..., description="encrypt_uin"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_fav_song(euin, page, num, credential=credential)
    return ApiResponse.success(data=result)


async def user_fav_songlists(
    euin: str = Query(..., description="encrypt_uin"),
    page: int = Query(1, description="页码"),
    num: int = Query(10, description="数量"),
    request: Request = None,
):
    credential = get_credential(request) if request else None
    result = await qqmusic_api.user.get_fav_songlist(euin, page, num, credential=credential)
    return ApiResponse.success(data=result)


# Handler 注册表，供 app 按名称查找
HANDLERS = {
    "search_general": search_general,
    "search_complete": search_complete,
    "search_by_type": search_by_type,
    "song_query": song_query,
    "song_urls": song_urls,
    "song_detail": song_detail,
    "song_similar": song_similar,
    "song_labels": song_labels,
    "song_related_mv": song_related_mv,
    "singer_info": singer_info,
    "singer_desc": singer_desc,
    "singer_list": singer_list,
    "singer_songs": singer_songs,
    "singer_albums": singer_albums,
    "album_detail": album_detail,
    "album_songs": album_songs,
    "album_cover": album_cover,
    "songlist_detail": songlist_detail,
    "songlist_songs": songlist_songs,
    "top_detail": top_detail,
    "mv_detail": mv_detail,
    "mv_urls": mv_urls,
    "comment_count": comment_count,
    "comment_hot": comment_hot,
    "comment_new": comment_new,
    "lyric": lyric,
    "recommend_feed": recommend_feed,
    "recommend_guess": recommend_guess,
    "recommend_songlist": recommend_songlist,
    "recommend_newsong": recommend_newsong,
    "user_homepage": user_homepage,
    "user_vip": user_vip,
    "user_follow_singers": user_follow_singers,
    "user_fans": user_fans,
    "user_friends": user_friends,
    "user_fav_songs": user_fav_songs,
    "user_fav_songlists": user_fav_songlists,
}
