#!/usr/bin/env python3
"""
微信麦序机器人主程序入口
"""
import threading
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.mc_robot import McWeChatRobot
from core.wechat_api import WeChatIntegration
from web.app import create_app


def main():
    print("启动微信麦序机器人...")

    try:
        # 创建机器人实例
        robot = McWeChatRobot()
        print("机器人实例创建成功")

        # 创建Web应用
        app = create_app(robot)
        print("Web应用创建成功")

        # 在单独线程中启动Web服务
        web_thread = threading.Thread(target=lambda: app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False
        ))
        web_thread.daemon = True
        web_thread.start()
        print("Web服务器线程启动")

        # 创建微信集成实例
        wechat = WeChatIntegration(robot)
        print("微信集成实例创建成功")

        # 启动微信监听
        print("开始监听微信消息...")
        wechat.start_listening()

    except Exception as e:
        print(f"启动过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()