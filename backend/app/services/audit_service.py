"""审核服务"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.models.models import Patient, ChargeItem, AuditResult, AuditRule
from app.models.schemas import (
    PatientCreate, ChargeItemCreate, AuditResultCreate,
    PatientResponse, ChargeItemResponse, AuditResultResponse
)
from app.services.rule_engine import RuleEngine, DEFAULT_RULES


class AuditService:
    """审核服务类"""

    @staticmethod
    async def create_patient(db: AsyncSession, patient: PatientCreate) -> Patient:
        """创建患者"""
        db_patient = Patient(**patient.model_dump())
        db.add(db_patient)
        await db.commit()
        await db.refresh(db_patient)
        return db_patient

    @staticmethod
    async def get_patient(db: AsyncSession, patient_id: str) -> Optional[Patient]:
        """获取患者信息"""
        result = await db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_patients(db: AsyncSession, skip: int = 0, limit: int = 100):
        """获取患者列表"""
        result = await db.execute(
            select(Patient).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create_charge_item(db: AsyncSession, charge_item: ChargeItemCreate) -> ChargeItem:
        """创建收费项目"""
        db_charge = ChargeItem(**charge_item.model_dump())
        db.add(db_charge)
        await db.commit()
        await db.refresh(db_charge)
        return db_charge

    @staticmethod
    async def get_charge_items_by_patient(
        db: AsyncSession,
        patient_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChargeItem]:
        """获取患者的收费项目"""
        result = await db.execute(
            select(ChargeItem)
            .where(ChargeItem.patient_id == patient_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_charge_item(db: AsyncSession, charge_item_id: str) -> Optional[ChargeItem]:
        """获取单个收费项目"""
        result = await db.execute(
            select(ChargeItem).where(ChargeItem.id == charge_item_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_audit_result(
        db: AsyncSession,
        audit_result: AuditResultCreate
    ) -> AuditResult:
        """创建审核结果"""
        db_result = AuditResult(**audit_result.model_dump())
        db.add(db_result)
        await db.commit()
        await db.refresh(db_result)
        return db_result

    @staticmethod
    async def delete_audit_results_by_patient(db: AsyncSession, patient_id: str):
        """删除患者的所有审核结果（用于幂等性）"""
        # 获取患者的所有收费项目ID
        result = await db.execute(
            select(ChargeItem.id).where(ChargeItem.patient_id == patient_id)
        )
        charge_item_ids = [row[0] for row in result.all()]

        if charge_item_ids:
            # 删除这些收费项目的审核结果
            await db.execute(
                delete(AuditResult).where(AuditResult.charge_item_id.in_(charge_item_ids))
            )
            await db.commit()

    @staticmethod
    async def get_audit_results_by_charge_item(
        db: AsyncSession,
        charge_item_id: str
    ) -> List[AuditResult]:
        """获取收费项目的审核结果"""
        result = await db.execute(
            select(AuditResult).where(AuditResult.charge_item_id == charge_item_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_statistics(db: AsyncSession) -> Dict[str, Any]:
        """获取统计数据"""
        # 患者总数
        result = await db.execute(select(func.count(Patient.id)))
        total_patients = result.scalar()

        # 收费项目总数
        result = await db.execute(select(func.count(ChargeItem.id)))
        total_charge_items = result.scalar()

        # 违规数量
        result = await db.execute(
            select(func.count(AuditResult.id)).where(AuditResult.is_violation == True)
        )
        total_violations = result.scalar()

        # 规则总数
        result = await db.execute(select(func.count(AuditRule.id)))
        total_rules = result.scalar()

        # 违规率
        result = await db.execute(select(func.count(AuditResult.id)))
        total_audits = result.scalar()
        violation_rate = (total_violations / total_audits * 100) if total_audits > 0 else 0

        # 最近审核记录
        result = await db.execute(
            select(AuditResult)
            .order_by(AuditResult.created_at.desc())
            .limit(10)
        )
        recent_audits = result.scalars().all()

        return {
            "total_patients": total_patients,
            "total_charge_items": total_charge_items,
            "total_violations": total_violations,
            "total_rules": total_rules,
            "violation_rate": round(violation_rate, 2),
            "recent_audits": [
                {
                    "id": audit.id,
                    "is_violation": audit.is_violation,
                    "violation_type": audit.violation_type,
                    "created_at": audit.created_at.isoformat()
                }
                for audit in recent_audits
            ]
        }

    @staticmethod
    async def search_patients(
        db: AsyncSession,
        keyword: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Patient]:
        """搜索患者"""
        result = await db.execute(
            select(Patient).where(
                (Patient.name.contains(keyword)) |
                (Patient.id_card.contains(keyword))
            ).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def audit_patient_charges(
        db: AsyncSession,
        patient_id: str
    ) -> List[AuditResult]:
        """
        审核患者的所有收费项目
        先删除旧结果，再生成新结果（幂等性）
        """
        # 1. 删除该患者的所有旧审核结果
        await AuditService.delete_audit_results_by_patient(db, patient_id)

        # 2. 获取患者信息
        patient = await AuditService.get_patient(db, patient_id)
        if not patient:
            return []

        # 3. 获取收费项目
        charges = await AuditService.get_charge_items_by_patient(db, patient_id)
        if not charges:
            return []

        # 4. 获取所有启用的规则
        result = await db.execute(
            select(AuditRule).where(AuditRule.is_active == True)
        )
        rules = result.scalars().all()

        # 如果没有规则，使用默认规则（首次初始化）
        if not rules:
            rules = await AuditService.init_default_rules(db)

        # 5. 逐个审核收费项目
        audit_results = []
        for charge in charges:
            check_result = RuleEngine.check_charge_item(patient, charge, rules)

            audit_result = AuditResult(
                charge_item_id=charge.id,
                is_violation=check_result.is_violation,
                violation_type=check_result.violation_type,
                violation_description=check_result.violation_description,
                suggestion=check_result.suggestion,
                rule_id=check_result.rule_id
            )
            db.add(audit_result)
            audit_results.append(audit_result)

        await db.commit()

        # 刷新所有结果以获取ID
        for result in audit_results:
            await db.refresh(result)

        return audit_results

    @staticmethod
    async def init_default_rules(db: AsyncSession) -> List[AuditRule]:
        """初始化默认规则"""
        rules = []
        for rule_data in DEFAULT_RULES:
            rule = AuditRule(**rule_data)
            db.add(rule)
            rules.append(rule)

        await db.commit()

        # 刷新获取ID
        for rule in rules:
            await db.refresh(rule)

        print(f"✅ 初始化 {len(rules)} 条默认审核规则")
        return rules

    @staticmethod
    async def get_rules(db: AsyncSession) -> List[AuditRule]:
        """获取所有规则"""
        result = await db.execute(
            select(AuditRule).order_by(AuditRule.priority)
        )
        return result.scalars().all()
