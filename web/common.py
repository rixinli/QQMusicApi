"""Web 层公共定义，供 app 与 handlers 共用，避免循环导入"""

from time import time

from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

import qqmusic_api


class ApiResponseModel(BaseModel):
    """API响应数据模型"""

    code: int
    message: str
    data: object = None
    errors: list[str] | None = None
    timestamp: int


class ApiResponse(ORJSONResponse):
    """标准化API响应类"""

    def __init__(
        self,
        status_code: int = status.HTTP_200_OK,
        message: str = "Success",
        data: object = None,
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
        cls, data: object = None, message: str = "Success", status_code: int = status.HTTP_200_OK
    ) -> "ApiResponse":
        """构建成功响应"""
        return cls(status_code=status_code, message=message, data=data)

    @classmethod
    def error(
        cls, errors: str | list[str], message: str = "Error", status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> "ApiResponse":
        """构建错误响应"""
        return cls(status_code=status_code, message=message, errors=errors)


def get_credential(request: Request | None):
    """获取凭证"""
    if not request:
        return None
    try:
        credential = qqmusic_api.Credential.from_cookies_dict(request.cookies)
        qqmusic_api.get_session().credential = credential
        return credential
    except Exception:
        return None
