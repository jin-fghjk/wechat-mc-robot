"""
应用配置设置
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库配置
DATABASE = {
    'path': os.path.join(BASE_DIR, 'data', 'database', 'mc_robot.db'),
    'timeout': 30
}

# Web配置
WEB_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'secret_key': 'your-secret-key-here'
}

# 日志配置
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}