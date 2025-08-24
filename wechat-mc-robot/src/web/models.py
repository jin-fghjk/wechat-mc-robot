"""
Web数据模型
"""
from typing import List, Dict
import sqlite3


class McWebAdmin:
    """麦序机器人Web管理后台"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(base_dir, 'data', 'database', 'mc_robot.db')
        else:
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
                cursor.execute(
                    "SELECT id FROM settings WHERE group_id = ? AND key = ?",
                    (group_id, key)
                )
                existing = cursor.fetchone()

                if existing:
                    cursor.execute(
                        "UPDATE settings SET value = ? WHERE group_id = ? AND key = ?",
                        (value, group_id, key)
                    )
                else:
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