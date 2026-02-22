---
name: qqmusic-api
description: 调用 QQMusic Web API 获取音乐数据（搜索、歌曲、歌词、歌单、歌手、专辑、排行榜、MV、评论、推荐）。不做个人用户相关能力。通过 HTTP GET 请求调用，适合 MCP 或其他 Agent 集成。
---

# QQMusic API 使用指南

当用户需要 QQ 音乐相关数据（搜索、歌曲、歌手、专辑、歌单、排行榜、歌词、MV、评论、推荐）时，使用本技能调用 QQMusic Web API。不做个人用户相关能力（主页、VIP、关注、粉丝、好友、收藏等）。

**注意**：歌曲、歌手、专辑、歌单、MV、排行榜详情等接口通常需要先调用 `search/by_type` 或 `top/category` 获取正确的 ID/mid 后再调用，见下方「参数依赖与调用顺序」。

## 使用条件

1. **服务已启动**：QQMusic API 服务运行中，默认基地址 `http://localhost:8000`
2. 所有开放接口均无需登录

## 调用方式（MCP / Agent）

所有接口为 **GET** 请求，参数通过 query string 传递：

```
GET {base_url}{path}?param1=value1&param2=value2
```

响应格式：

```json
{
  "code": 200,
  "message": "Success",
  "data": { ... },
  "timestamp": 1234567890
}
```

成功时 `code` 为 200，业务数据在 `data` 中。

## 参数依赖与调用顺序（重要）

部分接口的参数（如 songid、mid、top_id、vids）**无法由用户直接提供**，需要 Agent 先从其他接口获取，再传入目标接口。

| 目标接口 | 所需参数 | 需先调用的接口 | 从返回中提取的字段 |
|----------|----------|----------------|--------------------|
| song/*, lyric, comment/* | ids / mids / songid / biz_id | `/search/by_type`（search_type=0 歌曲） | id/songid, mid/songmid |
| singer/* | mid / mids | `/search/by_type`（search_type=1 歌手） | mid / SingerMid |
| album/* | value / mid | `/search/by_type`（search_type=2 专辑） | albummid / albumid |
| songlist/* | songlist_id | `/search/by_type`（search_type=3 歌单） | dissid / disstid |
| mv/* | vids | `/search/by_type`（search_type=4 MV） | vid / Vid |
| top/detail | top_id | `/top/category` | 列表中项的 topId / top_id |

**示例**：获取「周杰伦」某首歌的歌词 → 先调用 `GET /search/by_type?keyword=周杰伦&search_type=0&num=5`，从 `data` 取首条 `id` 或 `mid`，再调用 `GET /lyric?value={该id}`。

**无依赖接口**（可直接调用）：`/search/hotkey`、`/search/complete`、`/search/general`、`/search/by_type`、`/singer/list`、`/top/category`、`/recommend/*`

## 端点速查（按需求选 path）

| 用户需求 | 路径 | 关键参数 |
|----------|------|----------|
| 热搜词 | `/search/hotkey` | 无 |
| 搜索建议/补全 | `/search/complete` | keyword |
| 综合搜索 | `/search/general` | keyword, page |
| 按类型搜索（歌/人/专辑等） | `/search/by_type` | keyword, search_type(0歌1人2专3单4MV7词8用户) |
| 歌曲基本信息 | `/song/query` | ids（逗号分隔） |
| 播放链接 | `/song/urls` | mids, file_type |
| 歌曲详情 | `/song/detail` | value(id 或 mid) |
| 相似歌曲 | `/song/similar` | songid |
| 歌曲标签 | `/song/labels` | songid |
| 相关 MV | `/song/related_mv` | songid, last_mvid(可选) |
| 歌手列表 | `/singer/list` | area, sex, genre |
| 歌手信息 | `/singer/info` | mid |
| 歌手歌曲 | `/singer/songs` | mid, page, num |
| 歌手专辑 | `/singer/albums` | mid, page, num |
| 歌手简介 | `/singer/desc` | mids（逗号分隔） |
| 专辑详情 | `/album/detail` | value |
| 专辑歌曲 | `/album/songs` | value, num, page |
| 专辑封面 | `/album/cover` | mid, size |
| 歌单详情 | `/songlist/detail` | songlist_id, num, page, onlysong |
| 歌单歌曲 | `/songlist/songs` | songlist_id |
| 排行榜分类 | `/top/category` | 无 |
| 排行榜详情 | `/top/detail` | top_id, num, page |
| MV 详情 | `/mv/detail` | vids（逗号分隔） |
| MV 播放链接 | `/mv/urls` | vids |
| 歌词 | `/lyric` | value, qrc, trans, roma |
| 评论数量 | `/comment/count` | biz_id |
| 热评 | `/comment/hot` | biz_id, page_num, page_size |
| 最新评论 | `/comment/new` | biz_id, page_num, page_size |
| 主页推荐 | `/recommend/feed` | 无 |
| 猜你喜欢 | `/recommend/guess` | 无 |
| 推荐歌单 | `/recommend/songlist` | 无 |
| 推荐新歌 | `/recommend/newsong` | 无 |

## 参数约定

- **ids / mids / vids**：多值用逗号分隔，如 `"123,456"`
- **search_type**：0=歌曲, 1=歌手, 2=专辑, 3=歌单, 4=MV, 7=歌词, 8=用户
- **file_type**：MP3_128, MP3_320, FLAC, OGG_320

## 错误处理

- `code` 非 200：请求失败，查看 `message` 和 `errors`
- 404：资源不存在
- 422：参数校验失败

## 完整 API 列表

详见同目录 [reference.md](reference.md)，与 `web/routes_config.py` 保持一致。
