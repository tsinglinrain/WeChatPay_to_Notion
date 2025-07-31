#!/bin/bash

# Docker 部署脚本
# 用于快速部署 WeChatPay_to_Notion 项目

set -e

echo "🚀 WeChatPay_to_Notion Docker 部署脚本"
echo "======================================"

# 检查是否安装了Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查是否安装了docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在"
    
    if [ -f ".env.template" ]; then
        echo "📋 复制 .env.template 到 .env"
        cp .env.template .env
        echo "✅ 请编辑 .env 文件并填入您的配置信息，然后重新运行此脚本"
        echo "📝 配置文件位置: $(pwd)/.env"
    else
        echo "❌ .env.template 文件也不存在，请检查项目完整性"
        exit 1
    fi
    exit 0
fi

# 验证环境变量配置
echo "🔍 验证配置..."
if ! python3 check_config.py 2>/dev/null; then
    echo "❌ 配置验证失败，请检查 .env 文件中的配置"
    echo "💡 您可以运行以下命令来检查配置："
    echo "   python3 check_config.py"
    exit 1
fi

echo "✅ 配置验证通过"

# 询问运行模式
echo ""
echo "请选择运行模式:"
echo "1) 构建并运行 (docker-compose up --build)"
echo "2) 后台运行 (docker-compose up -d --build)"
echo "3) 仅构建 (docker-compose build)"
echo "4) 停止运行 (docker-compose down)"

read -p "请输入选择 [1-4]: " choice

case $choice in
    1)
        echo "🏗️  构建并运行容器..."
        docker-compose up --build
        ;;
    2)
        echo "🏗️  构建并在后台运行容器..."
        docker-compose up -d --build
        echo "✅ 容器已在后台启动"
        echo "📋 查看日志: docker-compose logs -f"
        echo "🛑 停止容器: docker-compose down"
        ;;
    3)
        echo "🏗️  仅构建容器..."
        docker-compose build
        echo "✅ 构建完成"
        ;;
    4)
        echo "🛑 停止并移除容器..."
        docker-compose down
        echo "✅ 容器已停止"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 操作完成!"
