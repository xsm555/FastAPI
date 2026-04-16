# 环境变量配置
# app/core/config.py

import os
import secrets

# 1. 生成一个 32 字节的随机密钥 (Base64 编码)
SECRET_KEY = secrets.token_urlsafe(32)
# 2. 定义算法
ALGORITHM = "HS256"
# 3. Token 有效期 (例如 30 分钟)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Settings:
    # 数据库配置
    # 格式：mysql+aiomysql://用户:密码@主机:端口/数据库名
    # 注意：这里使用的是 aiomysql 驱动
    
    
    DEFAULT_DB_URL = "mysql+aiomysql://dev_user:mypassword*@db:3306/ecommerce_db?charset=utf8mb4"
    
    DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
    # 实际开发中，建议从环境变量读取，避免密码硬编码在代码里
    # import os
    # DATABASE_URL = os.getenv("DATABASE_URL", "默认值")

settings = Settings()