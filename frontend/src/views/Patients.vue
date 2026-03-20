<template>
  <div class="patients-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>患者列表</span>
              <el-button type="primary" @click="showAddPatient = true">
                <el-icon><Plus /></el-icon> 添加患者
              </el-button>
            </div>
          </template>

          <el-table :data="patients" v-loading="loading" stripe>
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="age" label="年龄" width="80" />
            <el-table-column prop="gender" label="性别" width="80" />
            <el-table-column prop="insurance_type" label="医保类型" width="120" />
            <el-table-column prop="id_card" label="身份证号" min-width="180" show-overflow-tooltip />
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewCharges(row)">
                  查看收费
                </el-button>
                <el-button type="success" size="small" @click="handleAuditPatient(row)">
                  审核
                </el-button>
                <el-button type="primary" link size="small" @click="addCharge(row)">
                  添加收费
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="stats-card">
          <template #header>
            <span>统计信息</span>
          </template>

          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_patients || 0 }}</div>
              <div class="stat-label">患者总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_charge_items || 0 }}</div>
              <div class="stat-label">收费项目</div>
            </div>
            <div class="stat-item">
              <div class="stat-value text-danger">{{ stats.total_violations || 0 }}</div>
              <div class="stat-label">违规项目</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.violation_rate || 0 }}%</div>
              <div class="stat-label">违规率</div>
            </div>
          </div>
        </el-card>

        <!-- 最近审核结果 -->
        <el-card shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span>最近审核</span>
          </template>

          <el-timeline>
            <el-timeline-item
              v-for="audit in stats.recent_audits?.slice(0, 5) || []"
              :key="audit.id"
              :type="audit.is_violation ? 'danger' : 'success'"
            >
              <p>{{ audit.is_violation ? '发现违规' : '审核通过' }}</p>
              <p class="text-muted">{{ audit.violation_type || '无违规' }}</p>
              <p class="text-muted text-small">{{ formatTime(audit.created_at) }}</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加患者对话框 -->
    <el-dialog v-model="showAddPatient" title="添加患者" width="500px">
      <el-form :model="patientForm" label-width="100px">
        <el-form-item label="姓名" required>
          <el-input v-model="patientForm.name" placeholder="请输入患者姓名" />
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="patientForm.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="patientForm.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="patientForm.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="医保类型">
          <el-select v-model="patientForm.insurance_type" placeholder="请选择" style="width: 100%;">
            <el-option label="职工医保" value="职工医保" />
            <el-option label="居民医保" value="居民医保" />
            <el-option label="新农合" value="新农合" />
            <el-option label="自费" value="自费" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddPatient = false">取消</el-button>
        <el-button type="primary" @click="submitPatient" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看收费项目对话框 -->
    <el-dialog v-model="showCharges" title="收费项目" width="800px">
      <el-table :data="selectedCharges" stripe>
        <el-table-column prop="item_name" label="项目名称" min-width="150" />
        <el-table-column prop="item_category" label="类别" width="100" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">¥{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="100">
          <template #default="{ row }">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="charge_date" label="收费日期" width="150">
          <template #default="{ row }">{{ formatDate(row.charge_date) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 添加收费项目对话框 -->
    <el-dialog v-model="showAddCharge" title="添加收费项目" width="500px">
      <el-form :model="chargeForm" label-width="100px">
        <el-form-item label="项目编码" required>
          <el-input v-model="chargeForm.item_code" placeholder="请输入项目编码" />
        </el-form-item>
        <el-form-item label="项目名称" required>
          <el-input v-model="chargeForm.item_name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目类别" required>
          <el-select v-model="chargeForm.item_category" placeholder="请选择" style="width: 100%;">
            <el-option label="药品" value="药品" />
            <el-option label="检查" value="检查" />
            <el-option label="治疗" value="治疗" />
            <el-option label="材料" value="材料" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" required>
          <el-input-number v-model="chargeForm.quantity" :min="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="单价" required>
          <el-input-number v-model="chargeForm.unit_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="科室">
          <el-input v-model="chargeForm.department" placeholder="请输入科室" />
        </el-form-item>
        <el-form-item label="医生姓名">
          <el-input v-model="chargeForm.doctor_name" placeholder="请输入医生姓名" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddCharge = false">取消</el-button>
        <el-button type="primary" @click="submitCharge" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 审核结果对话框 -->
    <el-dialog v-model="showAuditResult" title="审核结果" width="700px">
      <div v-if="auditResults.length > 0">
        <el-alert
          v-for="result in auditResults"
          :key="result.id"
          :title="result.is_violation ? '发现违规' : '审核通过'"
          :type="result.is_violation ? 'error' : 'success'"
          :description="result.violation_description || result.suggestion"
          show-icon
          style="margin-bottom: 12px;"
        >
          <template v-if="result.is_violation">
            <p><strong>违规类型:</strong> {{ result.violation_type }}</p>
            <p><strong>处理建议:</strong> {{ result.suggestion }}</p>
          </template>
        </el-alert>
      </div>
      <el-empty v-else description="暂无审核结果" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getPatients, createPatient, getPatientCharges, createChargeItem,
  auditPatient, getStatistics
} from '@/api'

const loading = ref(false)
const patients = ref([])
const stats = ref({})

const showAddPatient = ref(false)
const showCharges = ref(false)
const showAddCharge = ref(false)
const showAuditResult = ref(false)
const submitting = ref(false)

const selectedPatient = ref(null)
const selectedCharges = ref([])
const auditResults = ref([])

const patientForm = ref({
  name: '',
  age: 30,
  gender: '男',
  id_card: '',
  insurance_type: '职工医保'
})

const chargeForm = ref({
  item_code: '',
  item_name: '',
  item_category: '药品',
  quantity: 1,
  unit_price: 0,
  department: '',
  doctor_name: ''
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const [patientsData, statsData] = await Promise.all([
      getPatients(),
      getStatistics()
    ])
    patients.value = patientsData
    stats.value = statsData
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 提交患者
const submitPatient = async () => {
  if (!patientForm.value.name) {
    ElMessage.warning('请输入患者姓名')
    return
  }

  submitting.value = true
  try {
    await createPatient(patientForm.value)
    ElMessage.success('添加成功')
    showAddPatient.value = false
    patientForm.value = { name: '', age: 30, gender: '男', id_card: '', insurance_type: '职工医保' }
    loadData()
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

// 查看收费项目
const viewCharges = async (patient) => {
  selectedPatient.value = patient
  try {
    const charges = await getPatientCharges(patient.id)
    selectedCharges.value = charges
    showCharges.value = true
  } catch (error) {
    ElMessage.error('获取收费项目失败')
  }
}

// 添加收费项目
const addCharge = (patient) => {
  selectedPatient.value = patient
  chargeForm.value = {
    item_code: '',
    item_name: '',
    item_category: '药品',
    quantity: 1,
    unit_price: 0,
    department: '',
    doctor_name: ''
  }
  showAddCharge.value = true
}

// 提交收费项目
const submitCharge = async () => {
  if (!chargeForm.value.item_code || !chargeForm.value.item_name) {
    ElMessage.warning('请填写完整信息')
    return
  }

  submitting.value = true
  try {
    await createChargeItem(selectedPatient.value.id, {
      ...chargeForm.value,
      total_amount: chargeForm.value.quantity * chargeForm.value.unit_price,
      charge_date: new Date().toISOString()
    })
    ElMessage.success('添加成功')
    showAddCharge.value = false
    loadData()
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

// 审核患者
const handleAuditPatient = async (patient) => {
  try {
    await ElMessageBox.confirm(`确定要审核患者 "${patient.name}" 的所有收费项目吗？`, '确认审核', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await auditPatient(patient.id)
    auditResults.value = res.results
    showAuditResult.value = true
    ElMessage.success(res.message)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('审核失败: ' + error.message)
    }
  }
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.patients-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-card :deep(.el-card__body) {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-value.text-danger {
  color: #f56c6c;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.text-muted {
  color: #909399;
  font-size: 13px;
  margin-top: 4px;
}

.text-small {
  font-size: 12px;
}
</style>
