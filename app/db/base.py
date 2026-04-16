# app/db/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()
# declarative_base() 是 SQLAlchemy 提供的一个函数，用于创建一个基类，所有的 ORM 模型都应该继承这个基类。
# ORM模型是指使用 SQLAlchemy 定义的 Python 类，这些类映射到数据库中的表。通过继承 Base 类，我们可以定义各种模型类，每个模型类对应数据库中的一张表。
# 这样做的好处是可以统一管理模型的元数据，并且在创建数据库表时，SQLAlchemy 会根据这些模型自动生成相应的表结构。