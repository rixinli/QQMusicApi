# 路由 Swagger 参数盘查

## 盘查结果（已完成）

| 路径 | 必填参数 | 处理方式 |
|------|----------|----------|
| /search/hotkey | 无 | Parser（仅 2 个无参路由保留） |
| /search/complete | keyword | handler ✓ |
| /search/general | keyword | handler ✓ |
| /song/similar | songid | handler ✓ |
| /song/labels | songid | handler ✓ |
| /song/related_mv | songid | handler ✓ |
| /singer/info | mid | handler ✓ |
| /singer/desc | mids | handler ✓ |
| /album/cover | mid | handler ✓ |
| /songlist/detail | songlist_id | handler ✓ |
| /songlist/songs | songlist_id | handler ✓ |
| /top/category | 无 | Parser |
| /top/detail | top_id | handler ✓ |
| /mv/detail | vids | handler ✓ |
| /mv/urls | vids | handler ✓ |
| /comment/count | biz_id | handler ✓ |
| /comment/hot | biz_id | handler ✓ |
| /comment/new | biz_id | handler ✓ |

## 保留 Parser 的无参路由：/search/hotkey、/top/category
