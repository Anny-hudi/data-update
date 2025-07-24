# database模块初始化
from .connection import DatabaseManager

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

__all__ = ['DatabaseManager', 'db_manager']