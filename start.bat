@echo off
chcp 65001 >nul
title 医保智能审核系统启动脚本

echo 🏥 医保智能审核系统启动脚本
echo ================================
echo.

:: 检查 Docker
where docker >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Docker，请先安装 Docker Desktop
    pause
    exit /b 1
)

where docker-compose >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 docker-compose，请检查 Docker 安装
    pause
    exit /b 1
)

:: 显示菜单
echo 请选择操作:
echo 1. 启动所有服务
echo 2. 只启动数据库
echo 3. 停止所有服务
echo 4. 重启服务
echo 5. 查看日志
echo 6. 清理数据（警告：会删除所有数据）
echo 7. 退出
echo.

set /p choice="请输入选项 (1-7): "

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_db
if "%choice%"=="3" goto stop_all
if "%choice%"=="4" goto restart
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto clean
if "%choice%"=="7" goto end

echo 无效选项
pause
goto end

:start_all
echo 🚀 启动所有服务...
docker-compose up -d
echo.
echo ✅ 服务启动完成！
echo 📱 前端界面: http://localhost:3000
echo 🔌 后端API: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
pause
goto end

:start_db
echo 🗄️ 启动数据库服务...
docker-compose up -d postgres qdrant
echo ✅ 数据库服务已启动
echo PostgreSQL: localhost:5432
echo Qdrant: localhost:6333
pause
goto end

:stop_all
echo 🛑 停止所有服务...
docker-compose down
echo ✅ 服务已停止
pause
goto end

:restart
echo 🔄 重启服务...
docker-compose down
timeout /t 2 /nobreak >nul
docker-compose up -d
echo ✅ 服务已重启
pause
goto end

:logs
docker-compose logs -f
goto end

:clean
echo ⚠️  警告：这将删除所有数据！
set /p confirm="确定要继续吗？(yes/no): "
if /i "%confirm%"=="yes" (
    docker-compose down -v
    if exist uploads (
        del /f /q uploads\*
    )
    echo ✅ 数据已清理
) else (
    echo 已取消
)
pause
goto end

:end
