#!/usr/bin/env python3
"""
配置迁移脚本
帮助用户从YAML配置迁移到环境变量配置
"""

import os
import yaml
from pathlib import Path


def migrate_yaml_to_env():
    """从YAML配置文件迁移到.env文件"""
    
    # 查找YAML配置文件
    yaml_files = [
        "config_private.yaml",
        "config_private_163.yaml", 
        "config_private_lisongyan.yaml",
        "config_private_rain.yaml"
    ]
    
    yaml_config = None
    yaml_file_used = None
    
    for yaml_file in yaml_files:
        if os.path.exists(yaml_file):
            try:
                with open(yaml_file, "r", encoding="utf-8") as file:
                    yaml_config = yaml.safe_load(file)
                    yaml_file_used = yaml_file
                    print(f"✅ 找到YAML配置文件: {yaml_file}")
                    break
            except Exception as e:
                print(f"❌ 读取 {yaml_file} 失败: {e}")
                continue
    
    if not yaml_config:
        print("❌ 没有找到有效的YAML配置文件")
        print("支持的文件名:", ", ".join(yaml_files))
        return False
    
    # 检查.env文件是否已存在
    if os.path.exists(".env"):
        overwrite = input("⚠️  .env文件已存在，是否覆盖? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("⏹️  迁移已取消")
            return False
    
    # 提取配置信息
    try:
        email_config = yaml_config.get("email_config", {})
        notion_config = yaml_config.get("notion_config", {})
        
        # 处理不同的键名格式
        username = email_config.get("imap_url") or email_config.get("username") or email_config.get("email")
        password = email_config.get("password")
        imap_url = email_config.get("username") or email_config.get("imap_url") or email_config.get("server")
        
        database_id = notion_config.get("database_id")
        token = notion_config.get("token")
        
        # 验证必需字段
        if not all([username, password, imap_url, database_id, token]):
            print("❌ YAML配置文件中缺少必需的字段")
            print(f"找到的配置:")
            print(f"  username: {username}")
            print(f"  password: {'***' if password else 'None'}")
            print(f"  imap_url: {imap_url}")
            print(f"  database_id: {database_id}")
            print(f"  token: {'***' if token else 'None'}")
            return False
        
        # 创建.env文件内容
        env_content = f"""# 环境变量配置文件 - 从 {yaml_file_used} 迁移而来
# 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 邮箱配置
EMAIL_USERNAME={username}
EMAIL_PASSWORD={password}
EMAIL_IMAP_URL={imap_url}

# Notion配置
NOTION_DATABASE_ID={database_id}
NOTION_TOKEN={token}
"""
        
        # 写入.env文件
        with open(".env", "w", encoding="utf-8") as file:
            file.write(env_content)
        
        print("🎉 迁移成功!")
        print(f"✅ 已从 {yaml_file_used} 创建 .env 文件")
        print("✅ 配置信息:")
        print(f"   EMAIL_USERNAME: {username}")
        print(f"   EMAIL_PASSWORD: {'*' * len(password)}")
        print(f"   EMAIL_IMAP_URL: {imap_url}")
        print(f"   NOTION_DATABASE_ID: {database_id}")
        print(f"   NOTION_TOKEN: {token[:20]}...{token[-5:] if len(token) > 25 else token}")
        
        # 建议备份原文件
        print(f"\n💡 建议:")
        print(f"   1. 测试新配置是否正常工作: python check_config.py")
        print(f"   2. 确认正常后可以删除或备份原YAML文件: {yaml_file_used}")
        print(f"   3. 运行程序: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        return False


def main():
    print("YAML to ENV 配置迁移工具")
    print("=" * 50)
    
    if migrate_yaml_to_env():
        print("\n🎉 迁移完成!")
    else:
        print("\n❌ 迁移失败，请检查错误信息并重试")


if __name__ == "__main__":
    main()
