"""患者管理路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import (
    PatientCreate, PatientResponse,
    ChargeItemCreate, ChargeItemResponse
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/patients", tags=["患者管理"])


@router.post("", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建患者"""
    db_patient = await AuditService.create_patient(db, patient)
    return db_patient


@router.get("", response_model=List[PatientResponse])
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取患者列表"""
    patients = await AuditService.get_patients(db, skip=skip, limit=limit)
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取单个患者信息"""
    patient = await AuditService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    return patient


@router.post("/{patient_id}/charges", response_model=ChargeItemResponse)
async def create_charge_item(
    patient_id: str,
    charge_item: ChargeItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """为患者添加收费项目"""
    # 验证患者存在
    patient = await AuditService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")

    # 设置患者ID
    charge_item.patient_id = patient_id

    db_charge = await AuditService.create_charge_item(db, charge_item)
    return db_charge


@router.get("/{patient_id}/charges", response_model=List[ChargeItemResponse])
async def get_patient_charges(
    patient_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取患者的收费项目列表"""
    patient = await AuditService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")

    charges = await AuditService.get_charge_items_by_patient(db, patient_id, skip=skip, limit=limit)
    return charges


@router.get("/search", response_model=List[PatientResponse])
async def search_patients(
    keyword: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """搜索患者"""
    patients = await AuditService.search_patients(db, keyword, skip=skip, limit=limit)
    return patients
