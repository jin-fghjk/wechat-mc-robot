"""
Flask Web应用配置
"""
from flask import Flask
from flask_login import LoginManager
from .routes import init_routes

def create_app(robot_instance):
    app = Flask(__name__)
    app.config.from_pyfile('../../config/settings.py')

    # 初始化登录管理
    login_manager = LoginManager()
    login_manager.init_app(app)

    # 注册路由
    init_routes(app, robot_instance)

    return app