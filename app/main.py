# app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from fastapi.staticfiles import StaticFiles  # 1. 引入这个模块
import os
from app.core.response import success, fail # 自定义错误响应格式


app = FastAPI(title="电商后台", version="1.0.0")
# 最外层的 FastAPI 应用实例，所有的路由和事件都在这个实例上注册，title 和 version 是 API 的元信息，可以在自动生成的文档中看到
# FASTAPI 是一个现代、快速（高性能）的 Web 框架，用于构建 API，提供了自动生成文档、依赖注入等功能
# app = FastAPI(...) 是创建 FastAPI 应用实例，title 和 version 是 API 的元信息，可以在自动生成的文档中看到

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境请指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 捕获所有的 HTTPException (比如 404, 401)

@app.exception_handler(HTTPException) # 装饰器，注册一个异常处理器，捕获 HTTPException 类型的异常
async def http_exception_handler(request: Request, exc: HTTPException):
    return fail(message=exc.detail, code=exc.status_code)

# 2. 捕获数据验证错误 (比如前端少传了字段)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # exc.errors() 里面包含了具体哪个字段错了
    return fail(message=f"参数错误: {exc.errors()}", code=HTTP_422_UNPROCESSABLE_ENTITY)

# 3. 捕获所有未预料的服务器内部错误 (500)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # 这里可以打印日志，记录错误
    print(f"未捕获的异常: {exc}")
    return fail(message="服务器内部错误，请稍后再试", code=500)



# 1. 挂载路由
# 所有 /api/v1/... 的请求都会交给 api_router 处理
app.include_router(api_router, prefix="/api/v1")
# api_router 中已经包含了 products.py 定义的路由，所以 /api/v1/products/... 的请求会被正确处理
# prefix="/api/v1" 是为了给所有路由添加统一的前缀，方便版本管理和接口组织

# 2. 启动时自动建表
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # async with 是异步上下文管理器，确保连接正确关闭
        # engine.begin() 会自动处理事务，确保在执行完毕后提交或回滚
        # as conn 是获取到的数据库连接对象，可以用来执行 SQL 语句
        await conn.run_sync(Base.metadata.create_all)
        # await conn.run_sync(Base.metadata.create_all) 是异步执行创建表的操作
        # Base.metadata.create_all 是 SQLAlchemy 的方法，用于根据定义的模型创建数据库
    print("✅ 数据库表已检查/创建完成")

current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=current_dir + "/static"), name="static") # 2. 挂载静态文件目录
# app.mount("/static", StaticFiles(directory="app/static"), name="static") 也可以，但使用 os.path.join 更加稳健，适用于不同操作系统

@app.get("/")
async def root():
    return FileResponse(os.path.join(current_dir, "static", "index.html"),
        headers={"Cache-Control": "no-cache"}) # 3. 根路径返回静态 HTML 文件，headers={"Cache-Control": "no-cache"} 是为了确保浏览器每次都从服务器获取最新的文件，而不是使用缓存

@app.get("/hello")
async def hello():
    return {"message": "Hello, World!!!!"}