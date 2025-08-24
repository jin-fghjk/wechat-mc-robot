"""
数据库模型定义
"""


class DatabaseModels:
    """数据库表结构设计"""

    # 群组表
    groups_table = """
    CREATE TABLE groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT UNIQUE NOT NULL,      -- 群号码
        group_name TEXT,                    -- 群名称
        wxid TEXT,                          -- 群wxid
        member_count INTEGER,               -- 群人数
        status TEXT DEFAULT 'active',       -- 状态
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """

    # 麦序表
    mc_queue_table = """
    CREATE TABLE mc_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT NOT NULL,             -- 群号码
        user_id TEXT NOT NULL,              -- 用户ID
        user_name TEXT,                     -- 用户昵称
        position INTEGER NOT NULL,          -- 位置
        status TEXT DEFAULT 'waiting',      -- 状态
        join_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups (group_id)
    )
    """

    # 报备表
    reports_table = """
    CREATE TABLE reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT NOT NULL,             -- 群号码
        user_id TEXT NOT NULL,              -- 用户ID
        report_type TEXT NOT NULL,          -- 报备类型
        report_time DATETIME,               -- 报备时间
        status TEXT DEFAULT 'pending',      -- 状态
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups (group_id)
    )
    """

    # 置顶表
    top_list_table = """
    CREATE TABLE top_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT NOT NULL,             -- 群号码
        group_name TEXT,                    -- 群名称
        wxid TEXT,                          -- 群wxid
        start_time DATETIME,                -- 开始时间
        end_time DATETIME,                  -- 截止时间
        status TEXT DEFAULT 'active',       -- 状态
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups (group_id)
    )
    """

    # 管理员表
    admins_table = """
    CREATE TABLE admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,       -- 用户ID
        user_name TEXT,                     -- 用户昵称
        wxid TEXT,                          -- 用户wxid
        permission_level INTEGER DEFAULT 1, -- 权限级别
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """

    # 系统设置表
    settings_table = """
    CREATE TABLE settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT NOT NULL,             -- 群号码
        key TEXT NOT NULL,                  -- 设置键
        value TEXT,                         -- 设置值
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups (group_id)
    )
    """