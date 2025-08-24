"""
数据库初始化和管理
"""
import sqlite3
import os
from .models import DatabaseModels

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(base_dir, 'data', 'database', 'mc_robot.db')
        else:
            self.db_path = db_path

        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建所有表
        models = DatabaseModels()
        tables = [
            models.groups_table,
            models.mc_queue_table,
            models.reports_table,
            models.top_list_table,
            models.admins_table,
            models.settings_table
        ]

        for table_sql in tables:
            try:
                cursor.execute(table_sql)
                print(f"成功创建表: {table_sql.split()[2]}")
            except sqlite3.Error as e:
                print(f"创建表时出错: {e}")

        conn.commit()
        conn.close()
        print("数据库初始化完成")

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)