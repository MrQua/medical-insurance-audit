"""规则引擎服务 - 基于简单规则的审核逻辑"""
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.models.models import Patient, ChargeItem, AuditRule


@dataclass
class RuleCheckResult:
    """规则检查结果"""
    is_violation: bool
    rule_id: Optional[str]
    violation_type: Optional[str]
    violation_description: Optional[str]
    suggestion: Optional[str]


class RuleEngine:
    """规则引擎 - 执行简单规则检查"""

    @staticmethod
    def check_charge_item(
        patient: Patient,
        charge_item: ChargeItem,
        rules: List[AuditRule]
    ) -> RuleCheckResult:
        """
        对单个收费项目进行规则检查
        按优先级排序，返回第一个触发的规则
        """
        # 按优先级排序规则
        sorted_rules = sorted(rules, key=lambda r: r.priority)

        for rule in sorted_rules:
            if not rule.is_active:
                continue

            # 检查项目类别是否匹配
            if rule.target_category and rule.target_category != charge_item.item_category:
                continue

            # 检查项目名称是否匹配
            if rule.target_item_pattern:
                if not re.search(rule.target_item_pattern, charge_item.item_name, re.IGNORECASE):
                    continue

            # 检查条件
            if RuleEngine._check_condition(patient, charge_item, rule):
                # 规则触发，生成违规信息
                description = RuleEngine._render_template(
                    rule.violation_description_template,
                    patient,
                    charge_item
                )
                suggestion = RuleEngine._render_template(
                    rule.suggestion_template or "请核实后处理",
                    patient,
                    charge_item
                )

                return RuleCheckResult(
                    is_violation=True,
                    rule_id=rule.id,
                    violation_type=rule.violation_type,
                    violation_description=description,
                    suggestion=suggestion
                )

        # 没有规则触发，返回正常
        return RuleCheckResult(
            is_violation=False,
            rule_id=None,
            violation_type=None,
            violation_description=None,
            suggestion="符合规定"
        )

    @staticmethod
    def _check_condition(patient: Patient, charge_item: ChargeItem, rule: AuditRule) -> bool:
        """检查规则条件是否满足"""
        if not rule.condition_field:
            # 没有条件字段，只要项目匹配就触发
            return True

        # 获取条件值
        if rule.condition_field == "gender":
            actual_value = patient.gender
        elif rule.condition_field == "age":
            actual_value = str(patient.age) if patient.age is not None else None
        elif rule.condition_field == "amount":
            actual_value = str(charge_item.total_amount)
        elif rule.condition_field == "item_name":
            actual_value = charge_item.item_name
        else:
            return False

        if actual_value is None:
            return False

        # 执行比较
        expected_value = rule.condition_value
        operator = rule.condition_operator or "eq"

        if operator == "eq":
            return actual_value == expected_value
        elif operator == "ne":
            return actual_value != expected_value
        elif operator == "gt":
            try:
                return float(actual_value) > float(expected_value)
            except (ValueError, TypeError):
                return False
        elif operator == "lt":
            try:
                return float(actual_value) < float(expected_value)
            except (ValueError, TypeError):
                return False
        elif operator == "in":
            return expected_value in actual_value
        elif operator == "not_in":
            return expected_value not in actual_value
        elif operator == "regex":
            return bool(re.search(expected_value, actual_value))

        return False

    @staticmethod
    def _render_template(template: str, patient: Patient, charge_item: ChargeItem) -> str:
        """渲染模板"""
        if not template:
            return ""

        return template.format(
            patient_name=patient.name or "未知",
            patient_gender=patient.gender or "未知",
            patient_age=patient.age or "未知",
            item_name=charge_item.item_name,
            item_category=charge_item.item_category,
            amount=charge_item.total_amount
        )


# 预定义的 10 条简单规则
DEFAULT_RULES = [
    {
        "rule_name": "前列腺检查性别限制",
        "rule_description": "前列腺相关检查只允许男性患者开立",
        "rule_type": "gender",
        "target_item_pattern": "前列腺",
        "target_category": "检查",
        "condition_field": "gender",
        "condition_operator": "ne",
        "condition_value": "男",
        "violation_type": "性别不符",
        "violation_description_template": "患者{patient_name}（{patient_gender}）不允许开立前列腺检查项目：{item_name}",
        "suggestion_template": "请核实患者性别或更换检查项目",
        "priority": 1
    },
    {
        "rule_name": "妇科检查性别限制",
        "rule_description": "妇科相关检查只允许女性患者开立",
        "rule_type": "gender",
        "target_item_pattern": "妇科|宫颈|乳腺",
        "target_category": "检查",
        "condition_field": "gender",
        "condition_operator": "ne",
        "condition_value": "女",
        "violation_type": "性别不符",
        "violation_description_template": "患者{patient_name}（{patient_gender}）不允许开立妇科检查项目：{item_name}",
        "suggestion_template": "请核实患者性别或更换检查项目",
        "priority": 1
    },
    {
        "rule_name": "儿童用药年龄限制",
        "rule_description": "部分药品不适用于12岁以下儿童",
        "rule_type": "age",
        "target_item_pattern": "吗啡|可待因|曲马多",
        "target_category": "药品",
        "condition_field": "age",
        "condition_operator": "lt",
        "condition_value": "12",
        "violation_type": "超范围用药",
        "violation_description_template": "患者{patient_name}（{patient_age}岁）为儿童，不宜使用{item_name}",
        "suggestion_template": "请更换适合儿童的药品或咨询药师",
        "priority": 2
    },
    {
        "rule_name": "老年人用药限制",
        "rule_description": "部分药品不适用于65岁以上老年人",
        "rule_type": "age",
        "target_item_pattern": "氨基比林|非那西丁",
        "target_category": "药品",
        "condition_field": "age",
        "condition_operator": "gt",
        "condition_value": "65",
        "violation_type": "超范围用药",
        "violation_description_template": "患者{patient_name}（{patient_age}岁）为老年人，慎用{item_name}",
        "suggestion_template": "请评估用药风险或更换替代药品",
        "priority": 2
    },
    {
        "rule_name": "CT检查单次金额限制",
        "rule_description": "单次CT检查金额超过500元需要审核",
        "rule_type": "amount",
        "target_item_pattern": "CT",
        "target_category": "检查",
        "condition_field": "amount",
        "condition_operator": "gt",
        "condition_value": "500",
        "violation_type": "超标准收费",
        "violation_description_template": "{item_name}金额{amount}元超过500元标准",
        "suggestion_template": "请核实收费标准或拆分检查项目",
        "priority": 3
    },
    {
        "rule_name": "高档药品审核",
        "rule_description": "单价超过1000元的药品需要重点审核",
        "rule_type": "amount",
        "target_category": "药品",
        "condition_field": "amount",
        "condition_operator": "gt",
        "condition_value": "1000",
        "violation_type": "高价药品",
        "violation_description_template": "{item_name}为高价药品，金额{amount}元",
        "suggestion_template": "请确认用药必要性及医保报销范围",
        "priority": 4
    },
    {
        "rule_name": "进口材料审核",
        "rule_description": "进口材料使用需要说明",
        "rule_type": "category",
        "target_item_pattern": "进口",
        "target_category": "材料",
        "condition_field": None,
        "condition_operator": None,
        "condition_value": None,
        "violation_type": "进口材料",
        "violation_description_template": "使用进口材料：{item_name}，金额{amount}元",
        "suggestion_template": "请确认已告知患者进口材料费用及报销政策",
        "priority": 5
    },
    {
        "rule_name": "造影剂使用限制",
        "rule_description": "造影剂检查需要评估肾功能",
        "rule_type": "custom",
        "target_item_pattern": "造影|增强",
        "target_category": "检查",
        "condition_field": None,
        "condition_operator": None,
        "condition_value": None,
        "violation_type": "特殊检查",
        "violation_description_template": "患者{patient_name}进行造影检查：{item_name}",
        "suggestion_template": "请确认已评估患者肾功能及过敏史",
        "priority": 6
    },
    {
        "rule_name": "抗生素使用审核",
        "rule_description": "广谱抗生素使用需要指征",
        "rule_type": "custom",
        "target_item_pattern": "头孢|青霉素|阿奇霉素",
        "target_category": "药品",
        "condition_field": None,
        "condition_operator": None,
        "condition_value": None,
        "violation_type": "抗生素使用",
        "violation_description_template": "开具抗生素：{item_name}",
        "suggestion_template": "请确认有明确感染指征及药敏结果",
        "priority": 7
    },
    {
        "rule_name": "重复检查提示",
        "rule_description": "短期内重复进行相同检查",
        "rule_type": "custom",
        "target_item_pattern": "CT|核磁|彩超",
        "target_category": "检查",
        "condition_field": None,
        "condition_operator": None,
        "condition_value": None,
        "violation_type": "重复检查",
        "violation_description_template": "近期内进行{item_name}检查",
        "suggestion_template": "请核实是否有必要重复检查，避免过度医疗",
        "priority": 8
    }
]
