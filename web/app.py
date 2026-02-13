"""WEB API Port (完整优化版) - 配置驱动路由"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

import qqmusic_api
from web.common import ApiResponse, ApiResponseModel, get_credential
from web.handlers import HANDLERS
from web.parser import Parser
from web.routes_config import ROUTES


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


async def _api_web(request: Request, module: str, func: str):
    """统一API请求处理（泛化路由）"""
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


def _create_parser_handler(module: str, func: str):
    """为标准路由创建 handler：使用 Parser 解析参数并调用 qqmusic_api"""

    async def handler(request: Request):
        get_credential(request)  # 若有 cookie 则注入 session，无则忽略

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

    return handler


# ==================== 配置驱动的路由注册 ====================
for spec in ROUTES:
    path = spec["path"]
    tags = spec["tags"]
    summary = spec["summary"]

    if "handler" in spec:
        endpoint = HANDLERS[spec["handler"]]
    else:
        module = spec["module"]
        func = spec["func"]
        endpoint = _create_parser_handler(module, func)

    app.add_api_route(
        path=path,
        endpoint=endpoint,
        methods=["GET"],
        tags=[tags],
        summary=summary,
        responses={
            200: {"model": ApiResponseModel},
            400: {"model": ApiResponseModel},
            401: {"model": ApiResponseModel},
            422: {"model": ApiResponseModel},
            500: {"model": ApiResponseModel},
        },
    )


# 泛化路由：放在最后，用于 /{module}/{func} 形式的动态调用
app.add_api_route(
    path="/{module}/{func}",
    endpoint=_api_web,
    methods=["GET"],
    summary="通用 API（模块/函数）",
    description="module 如 search/song/singer；func 为模块内函数名。示例: module=search, func=hotkey",
    responses={
        200: {"model": ApiResponseModel},
        400: {"model": ApiResponseModel},
        401: {"model": ApiResponseModel},
        422: {"model": ApiResponseModel},
        500: {"model": ApiResponseModel},
    },
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "web.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug",
    )
