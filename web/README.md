# Web Port 使用说明

## 1. 安装与运行

### 克隆仓库

```bash
# 克隆当前开发分支 Rixin-Personal-Dev
git clone -b Rixin-Personal-Dev https://github.com/l-1124/QQMusicApi
```

### 依赖安装

```bash
uv sync --group web
```

### 启动服务

```bash
uv run uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
```

### Docker

```bash
docker build . -t qq-music-api
docker run -d -p 8000:8000 qq-music-api
```

### Docker 内运行 API 测试

```bash
docker build -f Dockerfile.test -t qq-music-api-test .
docker run qq-music-api-test
```

## 2. API Endpoint

- **RESTful 路径**: 如 `GET /search/hotkey`、`GET /song/detail?value=xxx`（见 Swagger `/docs`）
- **泛化路径**: `GET /{module}/{func}?param=value`，示例: `GET /search/hotkey`、`GET /song/get_detail?value=12345`
- 路由由 `web/routes_config.py` 配置驱动，便于维护

## 3. 请求参数规则

### 类型转换规则

| 参数类型    | 示例值                          | 说明                                 |
| ----------- | ------------------------------- | ------------------------------------ |
| `int`       | `count=5`                       | 整数                                 |
| `bool`      | `is_vip=true`                   | `true`/`1`/`yes` 或 `false`/`0`/`no` |
| `datetime`  | `date=2023-10-01T12:34`         | ISO 8601 格式                        |
| `list[int]` | `id=1,2,3`                      | 逗号分隔的字符串                     |
| `Enum`      | `type=SongType.HIT`or`type=HIT` | 枚举名或值（见具体模块定义）         |
