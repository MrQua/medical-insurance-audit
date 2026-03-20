@echo off
chcp 65001 >nul
title 医保智能审核系统 - 后端启动脚本

setlocal EnableDelayedExpansion

:: 颜色定义
set "RED=[31m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "NC=[0m"

echo.
echo �� 医保智能审核系统 - 后端启动脚本
echo ======================================
echo.

:: 检查 uv
call :check_uv
if errorlevel 1 exit /b 1

:: 参数处理
if "%~1"=="" goto :dev
if "%~1"=="dev" goto :dev
if "%~1"=="prod" goto :prod
if "%~1"=="init" goto :init
if "%~1"=="test" goto :test
if "%~1"=="format" goto :format
if "%~1"=="lint" goto :lint
if "%~1"=="activate" goto :activate
if "%~1"=="help" goto :help
if "%~1"=="--help" goto :help
if "%~1"=="-h" goto :help

echo 未知命令: %~1
goto :help

:: 检查 uv
check_uv
call uv --version >nul 2>&1
if errorlevel 1 (
    echo �� 未找到 uv，请先安装:
    echo    powershell -c "irm https://astral.sh/uv/install.ps1 ^| iex"
    exit /b 1
)
for /f "tokens=*" %%a in ('uv --version') do set "UV_VERSION=%%a"
echo �� uv 已安装: !UV_VERSION!
exit /b 0

:: 初始化项目
:init
echo �� 初始化项目...
if not exist "uv.lock" (
    echo �� 生成 uv.lock 文件...
    call uv lock
)
echo �� 创建虚拟环境并安装依赖...
call uv sync --frozen
echo �� 项目初始化完成
goto :end

:: 启动开发服务器
:dev
call :check_uv
if errorlevel 1 exit /b 1

if not exist ".venv" (
    echo 虚拟环境不存在，先初始化...
    call :init
)

echo.
echo �� 启动开发服务器...
echo �� 提示: 使用 --reload 模式，代码修改会自动重启
echo.

:: 使用 uv run 自动激活虚拟环境
call uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
goto :end

:: 启动生产服务器
:prod
echo �� 启动生产服务器...
call uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
goto :end

:: 运行测试
:test
echo �� 运行测试...
call uv run pytest tests/ -v --tb=short
goto :end

:: 格式化代码
:format
echo �� 格式化代码...
call uv run black app/
call uv run ruff check --fix app/
goto :end

:: 代码检查
:lint
call uv run ruff check app/
goto :end

:: 激活虚拟环境提示
:activate
echo �� 虚拟环境信息:
echo    路径: %CD%\.venv
echo    Python: .venv\Scripts\python.exe
echo.
echo �� 手动激活命令:
echo    .venv\Scripts\activate.bat
echo.
echo �� 或者使用 uv run 直接运行命令:
echo    uv run python script.py
goto :end

:: 帮助
:help
echo 用法: run.bat [命令]
echo.
echo 命令:
echo   dev       启动开发服务器（默认）
echo   prod      启动生产服务器
echo   init      初始化项目（创建虚拟环境、安装依赖）
echo   test      运行测试
echo   format    格式化代码
echo   lint      运行代码检查
echo   activate  显示虚拟环境信息
echo   help      显示帮助
echo.
echo 示例:
echo   run.bat        启动开发服务器
echo   run.bat init   首次初始化

:end
echo.
pause
