"""数据模型定义"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Patient(Base):
    """患者信息表"""
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    id_card = Column(String(18), unique=True, nullable=True)
    insurance_type = Column(String(50), nullable=True, comment="医保类型")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    charge_items = relationship("ChargeItem", back_populates="patient", cascade="all, delete-orphan")


class ChargeItem(Base):
    """收费项目表"""
    __tablename__ = "charge_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    item_code = Column(String(50), nullable=False, comment="项目编码")
    item_name = Column(String(200), nullable=False, comment="项目名称")
    item_category = Column(String(50), nullable=False, comment="项目类别: 药品/检查/治疗/材料/其他")
    quantity = Column(Float, default=1.0, comment="数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    total_amount = Column(Float, nullable=False, comment="总金额")
    charge_date = Column(DateTime, nullable=False, comment="收费日期")
    department = Column(String(100), nullable=True, comment="科室")
    doctor_name = Column(String(100), nullable=True, comment="医生姓名")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    patient = relationship("Patient", back_populates="charge_items")
    audit_results = relationship("AuditResult", back_populates="charge_item", cascade="all, delete-orphan")


class AuditResult(Base):
    """审核结果表"""
    __tablename__ = "audit_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    charge_item_id = Column(String(36), ForeignKey("charge_items.id"), nullable=False)
    is_violation = Column(Boolean, nullable=False, default=False, comment="是否违规")
    violation_type = Column(String(100), nullable=True, comment="违规类型")
    violation_description = Column(Text, nullable=True, comment="违规描述")
    suggestion = Column(Text, nullable=True, comment="处理建议")
    rule_id = Column(String(36), nullable=True, comment="触发的规则ID")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    charge_item = relationship("ChargeItem", back_populates="audit_results")


class ChatHistory(Base):
    """聊天历史表"""
    __tablename__ = "chat_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), nullable=False, index=True, comment="会话ID")
    role = Column(String(20), nullable=False, comment="角色: user/assistant")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditRule(Base):
    """审核规则表"""
    __tablename__ = "audit_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    rule_name = Column(String(200), nullable=False, comment="规则名称")
    rule_description = Column(Text, nullable=True, comment="规则描述")
    rule_type = Column(String(50), nullable=False, comment="规则类型: gender/age/category/amount/custom")
    target_item_pattern = Column(String(200), nullable=True, comment="目标项目名称匹配模式")
    target_category = Column(String(50), nullable=True, comment="目标项目类别")
    condition_field = Column(String(50), nullable=True, comment="条件字段: gender/age/amount等")
    condition_operator = Column(String(20), nullable=True, comment="条件操作符: eq/ne/gt/lt/in/not_in")
    condition_value = Column(String(200), nullable=True, comment="条件值")
    violation_type = Column(String(100), nullable=False, comment="违规类型")
    violation_description_template = Column(Text, nullable=False, comment="违规描述模板")
    suggestion_template = Column(Text, nullable=True, comment="建议模板")
    is_active = Column(Boolean, default=True, comment="是否启用")
    priority = Column(Integer, default=100, comment="优先级")
    created_at = Column(DateTime, default=datetime.utcnow)
