"""
微信麦序机器人核心类
"""
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

# 添加正确的导入
from .models import DatabaseModels  # 添加这行
from .database import DatabaseManager  # 添加这行


class McWeChatRobot:
    """微信麦序机器人核心类"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(base_dir, 'data', 'database', 'mc_robot.db')
        else:
            self.db_path = db_path

        self.init_database()
        self.setup_logging()

    def init_database(self, cursor=None, conn=None):
        """初始化数据库"""
        # 修改这里，使用 DatabaseManager 而不是直接操作
        db_manager = DatabaseManager(self.db_path)
        db_manager.init_database()


    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("mc_robot.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("McWeChatRobot")

    def process_wechat_message(self, message: Dict) -> Optional[str]:
        """处理微信消息"""
        msg_type = message.get('type')
        content = message.get('content', '')
        sender = message.get('sender')
        group_id = message.get('group_id')

        self.logger.info(f"收到消息: {content} from {sender} in {group_id}")

        # 判断是否为命令
        if content.startswith('@小助手') or content.startswith('@麦序机器人'):
            # 提取命令部分
            command = content.split(' ', 1)[1] if ' ' in content else ""
            return self.process_command(group_id, sender, command)

        # 处理图片消息
        elif msg_type == 'image':
            return self.process_image_message(group_id, sender, message.get('image_path'))

        return None

    def process_command(self, group_id: str, user_id: str, command: str) -> str:
        """处理文本命令"""
        command = command.strip().lower()

        if command == "上麦":
            return self.add_to_queue(group_id, user_id)

        elif command == "下麦":
            return self.remove_from_queue(group_id, user_id)

        elif command == "查询麦序":
            return self.get_queue_status(group_id)

        elif command.startswith("报备"):
            report_type = command[2:].strip()
            return self.add_report(group_id, user_id, report_type)

        elif command == "置顶列表":
            return self.get_top_list(group_id)

        elif command.startswith("设置"):
            # 管理员命令
            if self.is_admin(user_id):
                setting_cmd = command[2:].strip()
                return self.process_setting_command(group_id, setting_cmd)
            else:
                return "您没有权限进行设置操作"

        else:
            return "未知命令，请使用：上麦、下麦、查询麦序、报备[类型]、置顶列表"

    def process_image_message(self, group_id: str, user_id: str, image_path: str) -> str:
        """处理图片消息"""
        # 这里可以集成OCR功能识别图片中的文字
        # 暂时模拟识别结果
        recognized_text = self.ocr_simulation(image_path)

        if "麦序" in recognized_text or "排队" in recognized_text:
            # 解析麦序信息并更新队列
            self.update_queue_from_image(group_id, recognized_text)
            return "已识别图片中的麦序信息，队列已更新"
        else:
            return "图片中未识别到麦序信息"

    def ocr_simulation(self, image_path: str) -> str:
        """模拟OCR识别（实际应使用Tesseract等OCR库）"""
        # 这里只是模拟，实际应使用OCR库识别图片中的文字
        return "麦序信息：1.用户A 2.用户B 3.用户C"

    def add_to_queue(self, group_id: str, user_id: str) -> str:
        """添加用户到麦序"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取当前最大位置
        cursor.execute(
            "SELECT MAX(position) FROM mc_queue WHERE group_id = ? AND status = 'waiting'",
            (group_id,)
        )
        max_position = cursor.fetchone()[0] or 0

        # 获取用户名
        user_name = self.get_user_name(user_id)

        # 插入新用户
        cursor.execute(
            "INSERT INTO mc_queue (group_id, user_id, user_name, position) VALUES (?, ?, ?, ?)",
            (group_id, user_id, user_name, max_position + 1)
        )

        conn.commit()
        conn.close()

        return f"您已成功上麦，当前位置：{max_position + 1}"

    def remove_from_queue(self, group_id: str, user_id: str) -> str:
        """从麦序移除用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 标记用户为已下麦
        cursor.execute(
            "UPDATE mc_queue SET status = 'done' WHERE group_id = ? AND user_id = ? AND status = 'waiting'",
            (group_id, user_id)
        )

        # 获取受影响的行数
        changes = conn.total_changes

        conn.commit()
        conn.close()

        if changes > 0:
            # 重新排序剩余用户
            self.reorder_queue(group_id)
            return "您已成功下麦"
        else:
            return "您不在麦序中"

    def reorder_queue(self, group_id: str):
        """重新排序麦序"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取所有等待中的用户
        cursor.execute(
            "SELECT id, user_id FROM mc_queue WHERE group_id = ? AND status = 'waiting' ORDER BY position",
            (group_id,)
        )
        users = cursor.fetchall()

        # 更新位置
        for index, (db_id, user_id) in enumerate(users, 1):
            cursor.execute(
                "UPDATE mc_queue SET position = ? WHERE id = ?",
                (index, db_id)
            )

        conn.commit()
        conn.close()

    def get_queue_status(self, group_id: str) -> str:
        """获取麦序状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT position, user_name FROM mc_queue WHERE group_id = ? AND status = 'waiting' ORDER BY position",
            (group_id,)
        )
        queue = cursor.fetchall()

        conn.close()

        if not queue:
            return "当前麦序为空"

        # 格式化输出
        result = "当前麦序：\n"
        for position, user_name in queue:
            result += f"    {position}. {user_name}\n"

        result += f"共{len(queue)}人在麦序中"
        return result

    def add_report(self, group_id: str, user_id: str, report_type: str) -> str:
        """添加报备"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取用户名
        user_name = self.get_user_name(user_id)

        # 插入报备记录
        cursor.execute(
            "INSERT INTO reports (group_id, user_id, report_type, report_time) VALUES (?, ?, ?, ?)",
            (group_id, user_id, report_type, datetime.now())
        )

        conn.commit()
        conn.close()

        return f"报备成功：{report_type}"

    def get_top_list(self, group_id: str) -> str:
        """获取置顶列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT group_name, start_time, end_time FROM top_list WHERE group_id = ? AND status = 'active'",
            (group_id,)
        )
        top_items = cursor.fetchall()

        conn.close()

        if not top_items:
            return "当前没有置顶项目"

        # 格式化输出
        result = "置顶列表：\n"
        for group_name, start_time, end_time in top_items:
            result += f"    {group_name} ({start_time} - {end_time})\n"

        return result

    def is_admin(self, user_id: str) -> bool:
        """检查用户是否为管理员"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM admins WHERE user_id = ? AND permission_level >= 1",
            (user_id,)
        )
        is_admin = cursor.fetchone()[0] > 0

        conn.close()
        return is_admin

    def process_setting_command(self, group_id: str, command: str) -> str:
        """处理设置命令"""
        # 这里可以实现各种设置命令
        # 例如：设置开始时间、截止时间、报备时间等

        if command.startswith("开始时间"):
            time_str = command[4:].strip()
            return self.update_setting(group_id, "start_time", time_str)

        elif command.startswith("截止时间"):
            time_str = command[4:].strip()
            return self.update_setting(group_id, "end_time", time_str)

        elif command.startswith("报备时间"):
            time_str = command[4:].strip()
            return self.update_setting(group_id, "report_time", time_str)

        else:
            return "未知设置命令"

    def update_setting(self, group_id: str, key: str, value: str) -> str:
        """更新设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 检查设置是否已存在
        cursor.execute(
            "SELECT id FROM settings WHERE group_id = ? AND key = ?",
            (group_id, key)
        )
        existing = cursor.fetchone()

        if existing:
            # 更新现有设置
            cursor.execute(
                "UPDATE settings SET value = ? WHERE group_id = ? AND key = ?",
                (value, group_id, key)
            )
        else:
            # 插入新设置
            cursor.execute(
                "INSERT INTO settings (group_id, key, value) VALUES (?, ?, ?)",
                (group_id, key, value)
            )

        conn.commit()
        conn.close()

        return f"已更新设置：{key} = {value}"

    def get_user_name(self, user_id: str) -> str:
        """获取用户名（实际应从微信API获取）"""
        # 这里只是模拟，实际应调用微信API获取用户信息
        return f"用户{user_id[-4:]}"

    def update_queue_from_image(self, group_id: str, recognized_text: str):
        """从图片识别结果更新队列"""
        # 这里实现从识别文本中解析麦序信息并更新数据库
        # 简化实现：清空当前队列并添加新用户
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 清空当前队列
        cursor.execute(
            "UPDATE mc_queue SET status = 'done' WHERE group_id = ? AND status = 'waiting'",
            (group_id,)
        )

        # 模拟添加新用户
        # 实际应根据识别文本解析用户信息
        for i in range(1, 4):
            cursor.execute(
                "INSERT INTO mc_queue (group_id, user_id, user_name, position) VALUES (?, ?, ?, ?)",
                (group_id, f"user{i}", f"用户{i}", i)
            )

        conn.commit()
        conn.close()


# Web管理后台类
class McWebAdmin:
    """麦序机器人Web管理后台"""

    def __init__(self, db_path: str = "mc_robot.db"):
        self.db_path = db_path

    def get_groups_list(self) -> List[Dict]:
        """获取群组列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT group_id, group_name, wxid, member_count, status FROM groups")
        groups = []
        for row in cursor.fetchall():
            groups.append({
                "group_id": row[0],
                "group_name": row[1],
                "wxid": row[2],
                "member_count": row[3],
                "status": row[4]
            })

        conn.close()
        return groups

    def get_top_list_data(self) -> List[Dict]:
        """获取置顶列表数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT group_id, group_name, wxid, start_time, end_time, status 
            FROM top_list 
            WHERE status = 'active'
        """)

        top_list = []
        for row in cursor.fetchall():
            top_list.append({
                "group_id": row[0],
                "group_name": row[1],
                "wxid": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "status": row[5]
            })

        conn.close()
        return top_list

    def update_group_settings(self, group_id: str, settings: Dict) -> bool:
        """更新群组设置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for key, value in settings.items():
                # 检查设置是否已存在
                cursor.execute(
                    "SELECT id FROM settings WHERE group_id = ? AND key = ?",
                    (group_id, key)
                )
                existing = cursor.fetchone()

                if existing:
                    # 更新现有设置
                    cursor.execute(
                        "UPDATE settings SET value = ? WHERE group_id = ? AND key = ?",
                        (value, group_id, key)
                    )
                else:
                    # 插入新设置
                    cursor.execute(
                        "INSERT INTO settings (group_id, key, value) VALUES (?, ?, ?)",
                        (group_id, key, value)
                    )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"更新设置失败: {e}")
            return False
        finally:
            conn.close()