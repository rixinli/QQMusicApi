---
name: qqmusic-api
description: 调用 QQMusic API 获取音乐数据。当用户需要搜索歌曲、获取歌词、查看歌单、歌手信息、排行榜、MV、评论或推荐内容时使用。支持综合搜索、按类型搜索、歌曲详情、播放链接等。
---

# QQMusic API 使用指南

当用户需要 QQ 音乐相关数据（搜索、歌曲、歌手、歌单、排行榜、歌词、MV、评论、推荐）时，使用本技能调用 QQMusic Web API。

## 前置条件

1. **服务已启动**：确保 QQMusic API 服务在运行，默认 `http://localhost:8000`
2. **用户模块需 Cookie**：`/user/vip`、`/user/friends` 等需登录 cookie；其他多数接口无需登录

## 调用方式

### 方式一：HTTP GET（通用）

所有接口为 `GET` 请求，参数以 query string 传递：

```
GET {base_url}/{path}?param1=value1&param2=value2
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

### 方式二：Python 客户端（推荐）

项目内 `tools/qqmusic_client.py` 提供封装：

```python
from tools.qqmusic_client import QQMusicClient

client = QQMusicClient()  # 可传 base_url 覆盖默认地址
result = client.search_general("周杰伦")
# result["data"] 为接口返回的数据
```

### 方式三：工具定义

`tools/qqmusic-tools.json` 包含完整工具定义，可被 Agent 框架（如 OpenAI function calling、Claude tools）解析后发起 HTTP 请求。每个 tool 的 `endpoint` 字段即为对应 API 路径。

## 常用场景速查

| 需求 | 工具/方法 | 关键参数 |
|------|----------|----------|
| 热搜词 | `qqmusic_search_hotkey` | 无 |
| 搜索建议 | `qqmusic_search_complete` | keyword |
| 综合搜索 | `qqmusic_search_general` | keyword, page |
| 按类型搜 | `qqmusic_search_by_type` | keyword, search_type (0歌1人2专3单4MV7词8用户) |
| 歌曲信息 | `qqmusic_song_query` | ids |
| 播放链接 | `qqmusic_song_urls` | mids, file_type |
| 歌词 | `qqmusic_lyric` | value, qrc/trans/roma |
| 歌单 | `qqmusic_songlist_detail` | songlist_id |
| 排行榜 | `qqmusic_top_category` → `qqmusic_top_detail` | top_id |
| 推荐 | `qqmusic_recommend_feed/guess/songlist/newsong` | 无 |
| 歌手信息 | `qqmusic_singer_info` | mid |
| MV | `qqmusic_mv_detail`, `qqmusic_mv_urls` | vids |
| 评论 | `qqmusic_comment_hot/new` | biz_id |

## 参数说明

- **ids / mids**：多值用逗号分隔，如 `"123,456"`
- **search_type**：0=歌曲, 1=歌手, 2=专辑, 3=歌单, 4=MV, 7=歌词, 8=用户
- **file_type**：MP3_128, MP3_320, FLAC, OGG_320
- **euin**：用户 encrypt_uin，用户相关接口需要

## 错误处理

- `code` 非 200 表示失败，查看 `message` 和 `errors`
- 401：需要登录（cookie）
- 404：资源不存在
- 422：参数验证失败

## 额外资源

- 完整 API 列表与参数，见 [reference.md](reference.md)
- 工具定义 JSON 见项目根目录 `tools/qqmusic-tools.json`
