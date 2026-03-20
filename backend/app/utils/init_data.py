"""初始化测试数据 - 数据工厂"""
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import async_session
from app.models.models import Patient, ChargeItem, AuditRule
from app.services.audit_service import AuditService


# 患者姓名库
FIRST_NAMES = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
LAST_NAMES = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀", "霞", "平"]

# 收费项目库 - 按照类别组织
CHARGE_ITEMS_POOL = {
    "药品": [
        ("YP001", "阿莫西林胶囊", 25.5),
        ("YP002", "奥美拉唑肠溶片", 35.8),
        ("YP003", "头孢克肟片", 48.0),
        ("YP004", "阿奇霉素片", 42.5),
        ("YP005", "盐酸氨溴索口服液", 28.0),
        ("YP006", "复方甘草片", 15.5),
        ("YP007", "布洛芬缓释胶囊", 22.0),
        ("YP008", "硝苯地平片", 18.5),
        ("YP009", "二甲双胍片", 32.0),
        ("YP010", "阿司匹林肠溶片", 12.5),
        ("YP011", "注射用青霉素钠", 8.5),
        ("YP012", "注射用头孢曲松钠", 45.0),
        ("YP013", "盐酸吗啡注射液", 120.0),
        ("YP014", "可待因片", 85.0),
        ("YP015", "曲马多片", 95.0),
        ("YP016", "人血白蛋白", 1200.0),
        ("YP017", "免疫球蛋白", 2500.0),
        ("YP018", "氨基比林片", 5.5),
        ("YP019", "非那西丁片", 8.0),
        ("YP020", "维生素C片", 3.5),
    ],
    "检查": [
        ("JC001", "CT胸部平扫", 280.0),
        ("JC002", "胃镜", 350.0),
        ("JC003", "腹部B超", 120.0),
        ("JC004", "心电图", 35.0),
        ("JC005", "血常规", 25.0),
        ("JC006", "尿常规", 15.0),
        ("JC007", "肝功能检查", 85.0),
        ("JC008", "肾功能检查", 75.0),
        ("JC009", "血脂检查", 65.0),
        ("JC010", "血糖检查", 20.0),
        ("JC011", "CT增强扫描", 580.0),
        ("JC012", "核磁共振平扫", 650.0),
        ("JC013", "核磁共振增强", 950.0),
        ("JC014", "全身PET-CT", 8000.0),
        ("JC015", "心脏彩超", 180.0),
        ("JC016", "颈部血管彩超", 220.0),
        ("JC017", "前列腺超声", 150.0),
        ("JC018", "妇科检查彩超", 160.0),
        ("JC019", "宫颈涂片检查", 85.0),
        ("JC020", "乳腺钼靶", 280.0),
    ],
    "治疗": [
        ("ZL001", "静脉输液", 15.0),
        ("ZL002", "肌肉注射", 8.0),
        ("ZL003", "皮下注射", 8.0),
        ("ZL004", "吸氧", 12.0),
        ("ZL005", "雾化吸入", 25.0),
        ("ZL006", "换药", 35.0),
        ("ZL007", "拆线", 25.0),
        ("ZL008", "导尿", 45.0),
        ("ZL009", "灌肠", 30.0),
        ("ZL010", "针灸治疗", 55.0),
        ("ZL011", "推拿按摩", 80.0),
        ("ZL012", "理疗", 65.0),
        ("ZL013", "高压氧治疗", 150.0),
        ("ZL014", "血液透析", 350.0),
        ("ZL015", "腹膜透析", 280.0),
    ],
    "材料": [
        ("CL001", "一次性输液器", 5.5),
        ("CL002", "一次性注射器", 2.5),
        ("CL003", "留置针", 15.0),
        ("CL004", "导尿包", 25.0),
        ("CL005", "换药包", 18.0),
        ("CL006", "纱布", 3.5),
        ("CL007", "胶布", 2.0),
        ("CL008", "进口心脏支架", 12000.0),
        ("CL009", "进口人工关节", 25000.0),
        ("CL010", "进口起搏器", 35000.0),
        ("CL011", "造影剂", 350.0),
    ]
}

DEPARTMENTS = ["内科", "外科", "妇产科", "儿科", "骨科", "心内科", "消化内科", "神经内科", "放射科", "检验科"]
DOCTORS = ["张医生", "李医生", "王医生", "刘医生", "陈医生", "赵医生", "孙医生", "周医生"]
INSURANCE_TYPES = ["职工医保", "居民医保", "新农合", "自费"]


async def init_test_data():
    """初始化测试数据 - 幂等生成"""
    async with async_session() as db:
        try:
            # 检查是否已有数据
            result = await db.execute(select(Patient))
            existing_patients = result.scalars().all()

            if existing_patients:
                print("✅ 测试数据已存在，跳过初始化")
                # 确保规则已初始化
                await AuditService.init_default_rules(db)
                return

            print("📝 正在创建测试数据...")

            # 1. 初始化规则
            await AuditService.init_default_rules(db)

            # 2. 生成10个患者
            patients = await _generate_patients(db, 10)

            # 3. 为每个患者生成100个收费项目
            total_charges = 0
            for patient in patients:
                charges = await _generate_charge_items_for_patient(db, patient, 100)
                total_charges += len(charges)

            print(f"✅ 测试数据创建完成: {len(patients)} 位患者, {total_charges} 条收费记录")

            # 4. 为每个患者执行一次审核（触发约10条规则）
            print("📝 正在执行初始审核...")
            total_violations = 0
            for patient in patients:
                results = await AuditService.audit_patient_charges(db, patient.id)
                violations = sum(1 for r in results if r.is_violation)
                total_violations += violations

            print(f"✅ 初始审核完成，共发现 {total_violations} 处违规")

        except Exception as e:
            await db.rollback()
            print(f"❌ 初始化测试数据失败: {e}")


async def _generate_patients(db: AsyncSession, count: int) -> list:
    """生成患者数据"""
    patients = []

    for i in range(count):
        # 生成姓名
        name = random.choice(FIRST_NAMES) + random.choice(LAST_NAMES)

        # 生成性别（女性多一点，便于测试妇科规则）
        gender = "女" if random.random() < 0.6 else "男"

        # 生成年龄（分布各个年龄段）
        if random.random() < 0.3:
            age = random.randint(1, 11)  # 儿童 30%
        elif random.random() < 0.6:
            age = random.randint(18, 64)  # 成年人 30%
        else:
            age = random.randint(65, 85)  # 老年人 40%

        # 生成身份证号
        id_card = f"110101{1950 + random.randint(0, 50):04d}{random.randint(1, 12):02d}{random.randint(1, 28):02d}{random.randint(1000, 9999):04d}"

        # 医保类型
        insurance_type = random.choice(INSURANCE_TYPES)

        patient = Patient(
            name=name,
            age=age,
            gender=gender,
            id_card=id_card,
            insurance_type=insurance_type
        )
        db.add(patient)
        patients.append(patient)

    await db.flush()  # 获取生成的ID
    return patients


async def _generate_charge_items_for_patient(db: AsyncSession, patient: Patient, count: int) -> list:
    """为单个患者生成收费项目"""
    charge_items = []
    base_date = datetime.now() - timedelta(days=random.randint(1, 30))

    for i in range(count):
        # 随机选择类别
        category = random.choice(list(CHARGE_ITEMS_POOL.keys()))

        # 随机选择项目
        item_code, item_name, unit_price = random.choice(CHARGE_ITEMS_POOL[category])

        # 随机数量
        quantity = random.randint(1, 5)

        # 计算总价
        total_amount = round(quantity * unit_price, 2)

        # 随机日期（患者就诊前后几天）
        charge_date = base_date + timedelta(hours=random.randint(0, 72))

        # 随机科室和医生
        department = random.choice(DEPARTMENTS)
        doctor_name = random.choice(DOCTORS)

        charge_item = ChargeItem(
            patient_id=patient.id,
            item_code=item_code,
            item_name=item_name,
            item_category=category,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            charge_date=charge_date,
            department=department,
            doctor_name=doctor_name
        )
        db.add(charge_item)
        charge_items.append(charge_item)

    await db.flush()
    return charge_items
