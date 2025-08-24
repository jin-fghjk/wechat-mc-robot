"""
微信相关配置
"""
# 企业微信配置（推荐）
WECHAT_CONFIG = {
    'corpid': 'your-corp-id',
    'corpsecret': 'your-corp-secret',
    'agentid': 'your-agent-id'
}

# 或者网页微信配置（有风险）
WEB_WECHAT_CONFIG = {
    'hot_reload': True,
    'status_storage_dir': 'data/wechat_status'
}