"""审核路由 - 基于规则引擎"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import AuditResponse, AuditResultResponse, AuditRuleResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit", tags=["违规审核"])


@router.post("/patient/{patient_id}", response_model=AuditResponse)
async def audit_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db)
):
    """审核指定患者的所有收费项目 - 基于规则引擎（幂等性：先删除旧结果再插入新结果）"""
    # 检查患者是否存在
    patient = await AuditService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")

    # 执行审核（自动处理幂等性）
    results = await AuditService.audit_patient_charges(db, patient_id)

    violation_count = sum(1 for r in results if r.is_violation)

    return AuditResponse(
        success=True,
        message=f"审核完成，共审核{len(results)}项，发现{violation_count}项违规",
        results=[AuditResultResponse.model_validate(r) for r in results]
    )


@router.get("/results/{charge_item_id}")
async def get_audit_results(
    charge_item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取收费项目的审核结果"""
    results = await AuditService.get_audit_results_by_charge_item(db, charge_item_id)
    return {
        "charge_item_id": charge_item_id,
        "results": [AuditResultResponse.model_validate(r) for r in results]
    }


@router.get("/statistics")
async def get_statistics(
    db: AsyncSession = Depends(get_db)
):
    """获取审核统计信息"""
    stats = await AuditService.get_statistics(db)
    return stats


@router.get("/rules", response_model=List[AuditRuleResponse])
async def get_audit_rules(
    db: AsyncSession = Depends(get_db)
):
    """获取所有审核规则"""
    rules = await AuditService.get_rules(db)
    return [AuditRuleResponse.model_validate(r) for r in rules]
