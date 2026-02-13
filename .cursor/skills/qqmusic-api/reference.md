# QQMusic API 完整接口参考

基地址默认：`http://localhost:8000`，所有接口 GET 请求。

## 搜索

| 路径 | 参数 | 说明 |
|-----|------|------|
| /search/hotkey | 无 | 热搜词 |
| /search/complete | keyword | 搜索补全 |
| /search/general | keyword, page=1, highlight=true | 综合搜索 |
| /search/by_type | keyword, search_type=0, num=10, page=1, highlight=true | 按类型搜索。search_type: 0歌1人2专3单4MV7词8用户 |

## 歌曲

| 路径 | 参数 | 说明 |
|-----|------|------|
| /song/query | ids | 歌曲信息，ids 逗号分隔 |
| /song/urls | mids, file_type=MP3_128 | 播放链接 |
| /song/detail | value | 歌曲详情，value 为 id 或 mid |
| /song/similar | songid | 相似歌曲 |
| /song/labels | songid | 歌曲标签 |
| /song/related_mv | songid | 相关 MV |

## 歌手

| 路径 | 参数 | 说明 |
|-----|------|------|
| /singer/list | area=-100, sex=-100, genre=-100 | 歌手列表。area: -100全,200内地,2港台,5欧美,4日,3韩；sex: -100全,0男,1女,2乐队 |
| /singer/info | mid | 歌手信息 |
| /singer/songs | mid, page=1, num=10 | 歌手歌曲 |
| /singer/albums | mid, page=1, num=10 | 歌手专辑 |
| /singer/desc | mids | 歌手简介，mids 逗号分隔 |

## 专辑

| 路径 | 参数 | 说明 |
|-----|------|------|
| /album/detail | value | 专辑详情 |
| /album/songs | value, num=10, page=1 | 专辑歌曲 |
| /album/cover | mid, size=300 | 封面链接，size: 150/300/500/800 |

## 歌单

| 路径 | 参数 | 说明 |
|-----|------|------|
| /songlist/detail | songlist_id, num=10, page=1, onlysong=false | 歌单详情 |
| /songlist/songs | songlist_id | 歌单全部歌曲 |

## 排行榜

| 路径 | 参数 | 说明 |
|-----|------|------|
| /top/category | 无 | 排行榜分类 |
| /top/detail | top_id, num=10, page=1 | 排行榜详情 |

## MV

| 路径 | 参数 | 说明 |
|-----|------|------|
| /mv/detail | vids | MV 详情，vids 逗号分隔 |
| /mv/urls | vids | MV 播放链接 |

## 歌词

| 路径 | 参数 | 说明 |
|-----|------|------|
| /lyric | value, qrc=false, trans=false, roma=false | 歌词。qrc 逐字, trans 翻译, roma 罗马音 |

## 评论

| 路径 | 参数 | 说明 |
|-----|------|------|
| /comment/count | biz_id | 评论数量 |
| /comment/hot | biz_id, page_num=1, page_size=15 | 热评 |
| /comment/new | biz_id, page_num=1, page_size=15 | 最新评论 |

## 推荐

| 路径 | 参数 | 说明 |
|-----|------|------|
| /recommend/feed | 无 | 主页推荐 |
| /recommend/guess | 无 | 猜你喜欢 |
| /recommend/songlist | 无 | 推荐歌单 |
| /recommend/newsong | 无 | 推荐新歌 |

## 用户（部分需 Cookie）

| 路径 | 参数 | 说明 |
|-----|------|------|
| /user/homepage | euin | 用户主页 |
| /user/vip | 无 | VIP 信息，需 cookie |
| /user/follow_singers | euin, page=1, num=10 | 关注歌手 |
| /user/fans | euin, page=1, num=10 | 粉丝列表 |
| /user/friends | page=1, num=10 | 好友列表，需 cookie |
| /user/fav_songs | euin, page=1, num=10 | 收藏歌曲 |
| /user/fav_songlists | euin, page=1, num=10 | 收藏歌单 |
