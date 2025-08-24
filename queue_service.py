"""
麦序队列服务
"""
import sqlite3
from typing import List, Dict


class QueueService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add_to_queue(self, group_id: str, user_id: str, user_name: str) -> int:
        """添加用户到麦序"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取当前最大位置
        cursor.execute(
            "SELECT MAX(position) FROM mc_queue WHERE group_id = ? AND status = 'waiting'",
            (group_id,)
        )
        max_position = cursor.fetchone()[0] or 0

        # 插入新用户
        cursor.execute(
            "INSERT INTO mc_queue (group_id, user_id, user_name, position) VALUES (?, ?, ?, ?)",
            (group_id, user_id, user_name, max_position + 1)
        )

        conn.commit()
        conn.close()

        return max_position + 1

    def remove_from_queue(self, group_id: str, user_id: str) -> bool:
        """从麦序移除用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE mc_queue SET status = 'done' WHERE group_id = ? AND user_id = ? AND status = 'waiting'",
            (group_id, user_id)
        )

        changes = conn.total_changes
        conn.commit()
        conn.close()

        if changes > 0:
            self.reorder_queue(group_id)
            return True
        return False

    def reorder_queue(self, group_id: str):
        """重新排序麦序"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, user_id FROM mc_queue WHERE group_id = ? AND status = 'waiting' ORDER BY position",
            (group_id,)
        )
        users = cursor.fetchall()

        for index, (db_id, user_id) in enumerate(users, 1):
            cursor.execute(
                "UPDATE mc_queue SET position = ? WHERE id = ?",
                (index, db_id)
            )

        conn.commit()
        conn.close()

    def get_queue_status(self, group_id: str) -> List[Dict]:
        """获取麦序状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT position, user_name, status FROM mc_queue WHERE group_id = ? ORDER BY position",
            (group_id,)
        )

        queue = []
        for position, user_name, status in cursor.fetchall():
            queue.append({
                "position": position,
                "user_name": user_name,
                "status": status
            })

        conn.close()
        return queue