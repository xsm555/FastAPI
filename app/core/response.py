from fastapi.responses import JSONResponse
from typing import Union, List

def success(data=None, message="操作成功", code=200):
    if data is None:
        pass
    elif isinstance(data, list):
        converted = []
        for item in data:
            if hasattr(item, "model_dump"):
                converted.append(item.model_dump())
            elif hasattr(item, "dict"):
                converted.append(item.dict())
            elif hasattr(item, "__dict__"):
                converted.append({k: v for k, v in item.__dict__.items() if not k.startswith("_")})
            else:
                converted.append(item)
        data = converted
    elif hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):
        data = data.dict()
    elif hasattr(data, "__dict__"):
        data = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}

    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )

def fail(message="操作失败", code=400):
    """失败响应"""
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": None
        }
    )





