"""
报备管理服务
"""
import sqlite3
from datetime import datetime
from typing import List, Dict


class ReportService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add_report(self, group_id: str, user_id: str, user_name: str, report_type: str) -> bool:
        """添加报备"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO reports (group_id, user_id, report_type, report_time) VALUES (?, ?, ?, ?)",
                (group_id, user_id, report_type, datetime.now())
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"添加报备失败: {e}")
            return False
        finally:
            conn.close()

    def get_reports(self, group_id: str) -> List[Dict]:
        """获取报备列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id, user_name, report_type, report_time, status FROM reports WHERE group_id = ? ORDER BY report_time DESC",
            (group_id,)
        )

        reports = []
        for user_id, user_name, report_type, report_time, status in cursor.fetchall():
            reports.append({
                "user_id": user_id,
                "user_name": user_name,
                "report_type": report_type,
                "report_time": report_time,
                "status": status
            })

        conn.close()
        return reports