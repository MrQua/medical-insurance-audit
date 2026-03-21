"""Pydantic 数据模型"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ========== 患者相关模型 ==========
class PatientBase(BaseModel):
    name: str = Field(..., description="患者姓名")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    id_card: Optional[str] = Field(None, description="身份证号")
    insurance_type: Optional[str] = Field(None, description="医保类型")


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 收费项目相关模型 ==========
class ChargeItemBase(BaseModel):
    item_code: str = Field(..., description="项目编码")
    item_name: str = Field(..., description="项目名称")
    item_category: str = Field(..., description="项目类别")
    quantity: float = Field(1.0, description="数量")
    unit_price: float = Field(..., description="单价")
    total_amount: float = Field(..., description="总金额")
    charge_date: datetime = Field(..., description="收费日期")
    department: Optional[str] = Field(None, description="科室")
    doctor_name: Optional[str] = Field(None, description="医生姓名")


class ChargeItemCreate(ChargeItemBase):
    patient_id: str


class ChargeItemResponse(ChargeItemBase):
    id: str
    patient_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChargeItemWithPatient(ChargeItemResponse):
    patient: Optional[PatientResponse] = None


# ========== 审核结果相关模型 ==========
class AuditResultBase(BaseModel):
    is_violation: bool = Field(False, description="是否违规")
    violation_type: Optional[str] = Field(None, description="违规类型")
    violation_description: Optional[str] = Field(None, description="违规描述")
    suggestion: Optional[str] = Field(None, description="处理建议")
    rule_id: Optional[str] = Field(None, description="触发的规则ID")


class AuditResultCreate(AuditResultBase):
    charge_item_id: str


class AuditResultResponse(AuditResultBase):
    id: str
    charge_item_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 审核规则相关模型 ==========
class AuditRuleBase(BaseModel):
    rule_name: str = Field(..., description="规则名称")
    rule_description: Optional[str] = Field(None, description="规则描述")
    rule_type: str = Field(..., description="规则类型")
    target_item_pattern: Optional[str] = Field(None, description="目标项目名称匹配模式")
    target_category: Optional[str] = Field(None, description="目标项目类别")
    condition_field: Optional[str] = Field(None, description="条件字段")
    condition_operator: Optional[str] = Field(None, description="条件操作符")
    condition_value: Optional[str] = Field(None, description="条件值")
    violation_type: str = Field(..., description="违规类型")
    violation_description_template: str = Field(..., description="违规描述模板")
    suggestion_template: Optional[str] = Field(None, description="建议模板")
    is_active: bool = Field(True, description="是否启用")
    priority: int = Field(100, description="优先级")


class AuditRuleCreate(AuditRuleBase):
    pass


class AuditRuleResponse(AuditRuleBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 聊天相关模型 ==========
class ChatMessage(BaseModel):
    role: str = Field(..., description="角色: user/assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")


class ChatResponse(BaseModel):
    message: str
    session_id: str


# ========== 审核请求模型 ==========
class AuditRequest(BaseModel):
    patient_id: Optional[str] = Field(None, description="患者ID")
    charge_item_ids: Optional[List[str]] = Field(None, description="指定审核的收费项目ID列表")


class AuditResponse(BaseModel):
    success: bool
    message: str
    results: List[AuditResultResponse]


# ========== 统计相关模型 ==========
class StatisticsResponse(BaseModel):
    total_patients: int
    total_charge_items: int
    total_violations: int
    total_rules: int
    violation_rate: float
    recent_audits: List[Dict[str, Any]]
