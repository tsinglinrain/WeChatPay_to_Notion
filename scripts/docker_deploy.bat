@echo off
rem Docker 部署脚本 (Windows版本)
rem 用于快速部署 WeChatPay_to_Notion 项目

echo 🚀 WeChatPay_to_Notion Docker 部署脚本
echo ======================================

rem 检查是否安装了Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

rem 检查是否安装了docker-compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose 未安装，请先安装 docker-compose
    pause
    exit /b 1
)

rem 检查 .env 文件是否存在
if not exist ".env" (
    echo ⚠️  .env 文件不存在
    
    if exist ".env.template" (
        echo 📋 复制 .env.template 到 .env
        copy ".env.template" ".env"
        echo ✅ 请编辑 .env 文件并填入您的配置信息，然后重新运行此脚本
        echo 📝 配置文件位置: %cd%\.env
    ) else (
        echo ❌ .env.template 文件也不存在，请检查项目完整性
    )
    pause
    exit /b 0
)

rem 验证环境变量配置
echo 🔍 验证配置...
python check_config.py >nul 2>&1
if errorlevel 1 (
    echo ❌ 配置验证失败，请检查 .env 文件中的配置
    echo 💡 您可以运行以下命令来检查配置：
    echo    python check_config.py
    pause
    exit /b 1
)

echo ✅ 配置验证通过
echo.

echo 请选择运行模式:
echo 1) 构建并运行 (docker-compose up --build)
echo 2) 后台运行 (docker-compose up -d --build)
echo 3) 仅构建 (docker-compose build)
echo 4) 停止运行 (docker-compose down)
echo.

set /p choice=请输入选择 [1-4]: 

if "%choice%"=="1" (
    echo 🏗️  构建并运行容器...
    docker-compose up --build
) else if "%choice%"=="2" (
    echo 🏗️  构建并在后台运行容器...
    docker-compose up -d --build
    echo ✅ 容器已在后台启动
    echo 📋 查看日志: docker-compose logs -f
    echo 🛑 停止容器: docker-compose down
) else if "%choice%"=="3" (
    echo 🏗️  仅构建容器...
    docker-compose build
    echo ✅ 构建完成
) else if "%choice%"=="4" (
    echo 🛑 停止并移除容器...
    docker-compose down
    echo ✅ 容器已停止
) else (
    echo ❌ 无效选择
    pause
    exit /b 1
)

echo.
echo 🎉 操作完成!
pause
