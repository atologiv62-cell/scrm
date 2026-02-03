<template>
  <div class="customer-detail-container" v-loading="loading">
    <!-- 1. 头部导航 -->
    <el-page-header @back="goBack" class="page-header mb-4">
      <template #content>
        <div class="flex items-center">
          <span class="text-large font-bold mr-3">
            {{ form.customer_name || '客户详情' }}
          </span>
          <el-tag :type="getSdkTagType(form.follow_status)">
            {{ form.follow_status || '待分配' }}
          </el-tag>
        </div>
      </template>
      <template #extra>
        <el-button @click="refreshData">刷新</el-button>
        <el-button type="primary" @click="handleSave">保存修改</el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20">
      <!-- 2. 左侧：基本信息与 AI 画像 -->
      <el-col :span="9">
        <el-card shadow="never" class="mb-4">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold">核心资料</span>
              <el-button type="primary" link @click="handleAIAnalysis" :loading="aiLoading">
                ✨ AI 客户画像分析
              </el-button>
            </div>
          </template>
          
          <!-- AI 分析结果展示 -->
          <div v-if="aiAnalysisResult" class="mb-4 bg-blue-50 p-3 rounded text-sm text-gray-700 leading-relaxed">
            <p class="font-bold mb-1 text-blue-600">✨ 分析报告：</p>
            <div style="white-space: pre-wrap;">{{ aiAnalysisResult }}</div>
          </div>

          <el-form :model="form" :rules="rules" ref="formRef" label-width="90px" label-position="left">
            <el-form-item label="客户名称" prop="customer_name">
              <el-input v-model="form.customer_name" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item label="微信号">
              <el-input v-model="form.wechat" />
            </el-form-item>
            <el-form-item label="客户来源">
              <el-select v-model="form.source" style="width: 100%" allow-create filterable>
                <el-option label="自然进店" value="自然进店" />
                <el-option label="抖音" value="抖音" />
                <el-option label="天猫" value="天猫" />
                <el-option label="转介绍" value="转介绍" />
              </el-select>
            </el-form-item>
            
            <el-divider content-position="center">意向与房产</el-divider>
            
            <el-form-item label="意向产品">
              <el-select v-model="form.intent_product_id" style="width: 100%" filterable clearable>
                <el-option v-for="item in productList" :key="item.id" :label="item.product_name" :value="item.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="装修进度">
              <el-select v-model="form.decoration_progress" style="width: 100%" allow-create filterable>
                <el-option label="未动工" value="未动工" />
                <el-option label="水电" value="水电" />
                <el-option label="泥木" value="泥木" />
                <el-option label="软装" value="软装" />
              </el-select>
            </el-form-item>
            <el-form-item label="小区地址">
              <el-input v-model="form.community" />
            </el-form-item>
            <el-form-item label="详细地址">
              <el-input v-model="form.address" type="textarea" :rows="2" />
            </el-form-item>
             <el-form-item label="流失竞品">
              <el-select v-model="form.competitor" style="width: 100%" allow-create filterable clearable>
                <el-option label="林氏" value="林氏" />
                <el-option label="顾家" value="顾家" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 3. 右侧：业务数据 Tabs -->
      <el-col :span="15">
        <el-card shadow="never">
          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <!-- 跟进记录 -->
            <el-tab-pane label="跟进记录" name="follow">
              <div class="bg-gray-50 p-4 rounded mb-4">
                <div class="flex justify-between items-center mb-2">
                  <span class="font-bold text-gray-600">写跟进</span>
                  <el-button type="warning" link size="small" @click="handleAIGenerateScript" :loading="aiScriptLoading">
                    ✨ AI 生成高转化话术
                  </el-button>
                </div>
                <el-input 
                  v-model="newFollow.content" 
                  type="textarea" 
                  :rows="3" 
                  placeholder="请输入跟进详情..."
                />
                <div class="mt-3 flex justify-between">
                  <div class="flex gap-2">
                    <el-select v-model="newFollow.tag" placeholder="跟进标签" style="width: 130px">
                      <el-option label="初次沟通" value="初次沟通" />
                      <el-option label="意向强烈" value="意向强烈" />
                      <el-option label="邀约到店" value="邀约到店" />
                      <el-option label="跟进中" value="跟进中" />
                    </el-select>
                    <el-date-picker 
                      v-model="newFollow.nextDate" 
                      type="date" 
                      placeholder="下次跟进" 
                      style="width: 140px"
                      value-format="YYYY-MM-DD"
                    />
                  </div>
                  <el-button type="primary" @click="handleAddFollow">提交跟进</el-button>
                </div>
              </div>

              <el-timeline class="mt-4 pl-2">
                <el-timeline-item 
                  v-for="(f, idx) in followList" 
                  :key="idx" 
                  :timestamp="f.create_time" 
                  placement="top"
                  :type="idx === 0 ? 'primary' : ''"
                >
                  <el-card shadow="hover" class="border-none bg-gray-50">
                    <div class="flex justify-between mb-1">
                      <span class="font-bold">{{ f.follow_tag || '跟进' }}</span>
                      <span class="text-xs text-gray-400">{{ f.follower_name }}</span>
                    </div>
                    <div class="text-gray-700">{{ f.follow_detail }}</div>
                    <div v-if="f.next_follow_time" class="mt-2 text-xs text-orange-500">
                      <el-icon class="mr-1"><AlarmClock /></el-icon>
                      下次计划: {{ f.next_follow_time }}
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>

            <!-- 订单信息 -->
            <el-tab-pane label="订单信息" name="order">
              <div class="mb-3 text-right">
                <el-button type="success" @click="handleAddOrder">新建订单</el-button>
              </div>
              <el-table :data="orderList" border stripe>
                <el-table-column prop="order_no" label="订单编号" width="150" />
                <el-table-column prop="product_name" label="商品" />
                <el-table-column prop="amount" label="金额">
                  <template #default="{row}">¥{{ row.amount }}</template>
                </el-table-column>
                <el-table-column prop="transaction_type" label="类型" width="100" />
                <el-table-column prop="create_time" label="下单时间" width="160" />
                <el-table-column label="操作" width="80" align="center">
                  <template #default="{row}">
                    <el-button link type="danger" @click="handleDeleteOrder(row.id)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <!-- 操作日志 -->
            <el-tab-pane label="操作日志" name="logs">
              <el-timeline class="mt-4">
                <el-timeline-item 
                  v-for="(log, idx) in logs" 
                  :key="idx" 
                  :timestamp="log.create_time"
                >
                  <div class="text-sm">
                    <span class="font-bold mr-2">{{ log.action_type }}</span>
                    <span class="text-gray-500 mr-2">({{ log.operator_name }})</span>
                    <span class="text-gray-600">{{ log.content }}</span>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 订单录入弹窗 -->
    <el-dialog title="录入订单" v-model="orderDialog.visible" width="500px">
      <el-form :model="orderForm" label-width="100px">
        <el-form-item label="订单编号">
          <el-input v-model="orderForm.order_no" placeholder="系统自动生成" disabled />
        </el-form-item>
        <el-form-item label="购买商品">
          <el-select v-model="orderForm.product_id" style="width: 100%" placeholder="请选择">
            <el-option v-for="p in productList" :key="p.id" :label="p.product_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="订单金额">
          <el-input-number v-model="orderForm.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="交易类型">
          <el-select v-model="orderForm.transaction_type" style="width: 100%" allow-create filterable default-first-option>
            <el-option label="微信支付" value="微信支付" />
            <el-option label="支付宝" value="支付宝" />
            <el-option label="京东" value="京东" />
            <el-option label="线下刷卡" value="线下刷卡" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否返现">
          <el-switch v-model="orderForm.is_cash_back" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="返现金额" v-if="orderForm.is_cash_back">
          <el-input-number v-model="orderForm.cash_back_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orderDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">提交订单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Hide, AlarmClock } from '@element-plus/icons-vue'
import { getCustomerList, updateCustomer, getCustomerLogs, getCustomerFollows, createCustomerFollow, callAI } from '@/api/customer'
import { getProductList } from '@/api/product'
import { getOrderList, createOrder, deleteOrder } from '@/api/order'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(false)
const activeTab = ref('follow')
const customerId = ref<number | null>(null)

// 数据源
const productList = ref<any[]>([])
const followList = ref<any[]>([])
const orderList = ref<any[]>([])
const logs = ref<any[]>([])

// 表单
const formRef = ref()
const form = reactive<any>({})
const rules = {
  customer_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }]
}

// AI 状态
const aiLoading = ref(false)
const aiScriptLoading = ref(false)
const aiAnalysisResult = ref('')

// 跟进表单
const newFollow = reactive({ content: '', nextDate: '', tag: '' })

// 订单表单
const orderDialog = reactive({ visible: false })
const orderForm = reactive({ 
  order_no: '', 
  product_id: null, 
  amount: 0, 
  transaction_type: '', 
  is_cash_back: 0,
  cash_back_amount: 0 
})

// --- 初始化 ---
onMounted(async () => {
  // 从路由参数或列表页传递的状态中获取ID（这里假设是独立路由，如果是弹窗模式则不需要这个文件）
  // 但为了兼容性，如果路由没ID，尝试从 History State 获取（Vue Router 特性）
  if (route.params.id) {
    customerId.value = Number(route.params.id)
    await initData()
  } else {
    // 如果没有 ID，通常说明是直接访问，建议返回列表
    // 或者如果您是在 index.vue 的弹窗里用这个组件，那逻辑会有所不同。
    // 这里的代码假设这是一个独立页面，如果没有ID则无法加载。
  }
  
  // 加载基础数据
  try {
    productList.value = await getProductList() as any
  } catch (e) {}
})

const initData = async () => {
  if (!customerId.value) return
  loading.value = true
  try {
    // 1. 获取客户详情 (由于后端暂无详情接口，用列表筛选模拟)
    // 实际项目中请让后端增加 GET /api/customers/{id}
    const res: any = await getCustomerList({ }) // 这里需要后端支持 ID 筛选，或者在前端 find
    // 临时方案：前端过滤
    const target = res.find((c: any) => c.id === customerId.value)
    if (target) {
      Object.assign(form, target)
    }
    
    // 2. 加载子数据
    await loadFollows()
    await loadOrders()
    await loadLogs()
  } catch (e) {
    console.error(e)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => initData()
const goBack = () => router.back()

// --- 业务逻辑 ---

const handleSave = async () => {
  if (!customerId.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      await updateCustomer(customerId.value!, form)
      ElMessage.success('保存成功')
      loadLogs()
    }
  })
}

// AI 分析
const handleAIAnalysis = async () => {
  aiLoading.value = true
  const pName = productList.value.find(p => p.id === form.intent_product_id)?.product_name || '未定'
  // 确保所有字段都有默认值，防止 undefined 导致 JS 报错
  const cName = form.customer_name || ''
  const prog = form.decoration_progress || ''
  const comm = form.community || ''
  
  const prompt = `分析客户画像：${cName}, 意向:${pName}, 装修:${prog}, 小区:${comm}. 给出成交概率及建议。`
  
  try {
    // 这里调用的是 api/customer.ts 中的 callAI
    const res: any = await callAI(prompt)
    if (res && res.result) {
      aiAnalysisResult.value = res.result
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('AI 分析请求失败，请检查后端日志')
  } finally {
    aiLoading.value = false
  }
}

// AI 话术
const handleAIGenerateScript = async () => {
  aiScriptLoading.value = true
  const pName = productList.value.find(p => p.id === form.intent_product_id)?.product_name || '家具'
  const cName = form.customer_name || '客户'
  const status = form.follow_status || ''
  
  const prompt = `生成微信跟进话术。客户:${cName}, 状态:${status}, 意向:${pName}. 要求亲切自然。`
  
  try {
    const res: any = await callAI(prompt)
    if (res && res.result) {
      newFollow.content = res.result
    }
  } catch (e) {
    ElMessage.error('AI 话术生成失败')
  } finally {
    aiScriptLoading.value = false
  }
}

// 跟进记录
const loadFollows = async () => { 
  if (customerId.value) followList.value = await getCustomerFollows(customerId.value) as any 
}
const handleAddFollow = async () => {
  if (!newFollow.content) return ElMessage.warning('请输入内容')
  if (!customerId.value) return
  
  try {
    await createCustomerFollow(customerId.value, {
      customer_id: customerId.value,
      follow_detail: newFollow.content,
      follow_tag: newFollow.tag,
      next_follow_time: newFollow.nextDate || null
    })
    ElMessage.success('提交成功')
    newFollow.content = ''
    loadFollows()
    loadLogs()
    // 更新头部状态
    form.follow_status = newFollow.tag || form.follow_status
  } catch (e) { console.error(e) }
}

// 订单
const loadOrders = async () => {
  if (customerId.value) orderList.value = await getOrderList(customerId.value) as any 
}
const handleAddOrder = () => {
  orderDialog.visible = true
  orderForm.order_no = 'OD' + Date.now()
  orderForm.amount = 0
  orderForm.product_id = null
}
const submitOrder = async () => {
  if (!orderForm.product_id || !orderForm.amount) return ElMessage.warning('请填写商品和金额')
  if (!customerId.value) return
  
  await createOrder({ ...orderForm, customer_id: customerId.value })
  ElMessage.success('订单创建成功')
  orderDialog.visible = false
  loadOrders()
  loadLogs()
}
const handleDeleteOrder = async (id: number) => {
  await deleteOrder(id)
  ElMessage.success('已删除')
  loadOrders()
}

// 日志
const loadLogs = async () => {
  if (customerId.value) logs.value = await getCustomerLogs(customerId.value) as any
}

const getSdkTagType = (s: string) => {
  if (s === '已成交') return 'success'
  if (s === '已流失') return 'info'
  return ''
}

const handleTabChange = (name: string) => {
  if (!customerId.value) return
  if (name === 'order') loadOrders()
  if (name === 'logs') loadLogs()
  if (name === 'follow') loadFollows()
}
</script>

<style scoped>
.customer-detail-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  background: #fff;
  padding: 15px 20px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}
</style>
```

**注意：** 这是一个独立的详情页组件。如果您想在路由中使用它，需要在 `router/index.ts` 中添加对应的路由规则，例如：

```typescript
{
  path: '/customer/detail/:id',
  component: () => import('@/views/customer/CustomerDetail.vue'),
  meta: { title: '客户详情', requiresAuth: true }
}