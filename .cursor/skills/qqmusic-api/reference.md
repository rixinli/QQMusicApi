# QQMusic API 接口参考

基于 `web/routes_config.py` 的开放接口，供 MCP 或其他 Agent 通过 HTTP GET 调用。

- **基地址**：`http://localhost:8000`（可按部署修改）
- **请求方式**：全部为 `GET`
- **响应格式**：`{ "code": 200, "message": "Success", "data": {...}, "timestamp": 1234567890 }`

---

## 搜索

| 路径 | 说明 | 参数 |
|------|------|------|
| `/search/hotkey` | 获取热搜词 | 无 |
| `/search/complete` | 搜索词补全 | `keyword`（必填） |
| `/search/general` | 综合搜索 | `keyword`（必填）, `page`=1, `highlight`=true |
| `/search/by_type` | 按类型搜索 | `keyword`（必填）, `search_type`=0, `num`=10, `page`=1, `highlight`=true |

`search_type`：0=歌曲, 1=歌手, 2=专辑, 3=歌单, 4=MV, 7=歌词, 8=用户

---

## 歌曲

| 路径 | 说明 | 参数 |
|------|------|------|
| `/song/query` | 获取歌曲信息 | `ids`（必填，逗号分隔） |
| `/song/urls` | 获取歌曲播放链接 | `mids`（必填，逗号分隔）, `file_type`=MP3_128 |
| `/song/detail` | 获取歌曲详情 | `value`（必填，歌曲 ID 或 mid） |
| `/song/similar` | 获取相似歌曲 | `songid`（必填） |
| `/song/labels` | 获取歌曲标签 | `songid`（必填） |
| `/song/related_mv` | 获取相关 MV | `songid`（必填）, `last_mvid`="" |

`file_type`：MP3_128, MP3_320, FLAC, OGG_320

---

## 歌手

| 路径 | 说明 | 参数 |
|------|------|------|
| `/singer/list` | 获取歌手列表 | `area`=-100, `sex`=-100, `genre`=-100 |
| `/singer/info` | 获取歌手信息 | `mid`（必填） |
| `/singer/songs` | 获取歌手歌曲 | `mid`（必填）, `page`=1, `num`=10 |
| `/singer/albums` | 获取歌手专辑 | `mid`（必填）, `page`=1, `num`=10 |
| `/singer/desc` | 获取歌手简介 | `mids`（必填，逗号分隔） |

`singer/list` 过滤：`area`=-100 全部/200 内地/2 港台/5 欧美/4 日本/3 韩国；`sex`=-100 全部/0 男/1 女/2 乐队；`genre`=-100 全部/7 流行/3 说唱/19 国风等

---

## 专辑

| 路径 | 说明 | 参数 |
|------|------|------|
| `/album/detail` | 获取专辑详情 | `value`（必填，专辑 ID 或 mid） |
| `/album/songs` | 获取专辑歌曲 | `value`（必填）, `num`=10, `page`=1 |
| `/album/cover` | 获取专辑封面 | `mid`（必填）, `size`=300 |

`size`：150, 300, 500, 800

---

## 歌单

| 路径 | 说明 | 参数 |
|------|------|------|
| `/songlist/detail` | 获取歌单详情 | `songlist_id`（必填）, `num`=10, `page`=1, `onlysong`=false |
| `/songlist/songs` | 获取歌单所有歌曲 | `songlist_id`（必填） |

---

## 排行榜

| 路径 | 说明 | 参数 |
|------|------|------|
| `/top/category` | 获取排行榜分类 | 无 |
| `/top/detail` | 获取排行榜详情 | `top_id`（必填）, `num`=10, `page`=1 |

---

## MV

| 路径 | 说明 | 参数 |
|------|------|------|
| `/mv/detail` | 获取 MV 详情 | `vids`（必填，逗号分隔） |
| `/mv/urls` | 获取 MV 播放链接 | `vids`（必填，逗号分隔） |

---

## 歌词

| 路径 | 说明 | 参数 |
|------|------|------|
| `/lyric` | 获取歌词 | `value`（必填，歌曲 ID 或 mid）, `qrc`=false, `trans`=false, `roma`=false |

`qrc` 逐字歌词，`trans` 翻译歌词，`roma` 罗马音

---

## 评论

| 路径 | 说明 | 参数 |
|------|------|------|
| `/comment/count` | 获取评论数量 | `biz_id`（必填，歌曲/专辑等业务 ID） |
| `/comment/hot` | 获取热评 | `biz_id`（必填）, `page_num`=1, `page_size`=15 |
| `/comment/new` | 获取最新评论 | `biz_id`（必填）, `page_num`=1, `page_size`=15 |

---

## 推荐

| 路径 | 说明 | 参数 |
|------|------|------|
| `/recommend/feed` | 获取主页推荐 | 无 |
| `/recommend/guess` | 猜你喜欢 | 无 |
| `/recommend/songlist` | 推荐歌单 | 无 |
| `/recommend/newsong` | 推荐新歌 | 无 |

---

## MCP 调用示例

```
GET {base_url}/search/general?keyword=周杰伦&page=1
GET {base_url}/song/urls?mids=002xxx&file_type=MP3_320
GET {base_url}/lyric?value=123456&trans=true
```

错误码：`code` 非 200 表示失败；404 资源不存在；422 参数校验失败。
