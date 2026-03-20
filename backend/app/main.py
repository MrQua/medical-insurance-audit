"""主应用入口"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models.database import init_db
from app.routers import (
    patients_router,
    chat_router,
    audit_router
)
from app.utils.init_data import init_test_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 正在启动医保智能审核系统...")

    # 初始化数据库
    await init_db()
    print("✅ 数据库初始化完成")

    # 初始化测试数据
    await init_test_data()

    print("✅ 系统启动完成")
    yield

    # 关闭时执行
    print("👋 系统关闭")


# 创建FastAPI应用
app = FastAPI(
    title="医保智能审核系统",
    description="基于规则引擎的医保收费违规智能审核系统",
    version="3.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(patients_router)
app.include_router(chat_router)
app.include_router(audit_router)

# 确保上传目录存在
os.makedirs("uploads", exist_ok=True)

# 静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """根路由"""
    return {
        "name": "医保智能审核系统",
        "version": "3.0.0",
        "engine": "rule-based",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "engine": "rule-based"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
