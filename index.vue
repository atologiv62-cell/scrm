<template>
  <div class="app-container">
    <el-card shadow="never">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="用户名">
          <el-input v-model="queryParams.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="queryParams.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getList">查询</el-button>
          <el-button type="primary" @click="handleAdd">新增用户</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-upload action="" :http-request="handleImport" :show-file-list="false" accept=".xlsx,.xls" style="display: inline-block; margin-left: 10px;">
            <el-button type="success" plain>导入</el-button>
          </el-upload>
        </div>
      </template>
      <el-table :data="tableData" border v-loading="loading">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="dept_name" label="所属门店" />
        <el-table-column prop="role_name" label="角色" />
        <el-table-column prop="post" label="岗位" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-switch v-model="scope.row.status" :active-value="1" :inactive-value="0" @change="handleStatus(scope.row)" />
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="handleEdit(scope.row)">修改</el-button>
            <el-button link type="warning" @click="handleResetPwd(scope.row)">重置密码</el-button>
            <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog :title="dialog.title" v-model="dialog.visible" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!dialog.isEdit">
             <el-input v-model="form.password" type="password" show-password placeholder="请输入登录密码" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="所属门店" prop="dept_id">
          <el-select v-model="form.dept_id" placeholder="请选择门店" style="width:100%" clearable filterable>
            <el-option v-for="item in deptList" :key="item.id" :label="item.dept_name" :value="item.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="请选择角色" style="width:100%" clearable>
            <el-option v-for="item in roleList" :key="item.id" :label="item.role_name" :value="item.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="岗位" prop="post">
             <el-select v-model="form.post" placeholder="请选择岗位" style="width:100%" clearable>
                <el-option label="店长" value="店长" />
                <el-option label="导购" value="导购" />
                <el-option label="客服" value="客服" />
                <el-option label="运营" value="运营" />
                <el-option label="管理员" value="管理员" />
             </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getUserList, createUser, updateUser, deleteUser, updateUserStatus, resetUserPassword, importUsers } from '@/api/user'
import { getDeptList } from '@/api/dept'
import { getRoleList } from '@/api/role'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const deptList = ref<any[]>([])
const roleList = ref<any[]>([])

const queryParams = reactive({ username: '', phone: '' })
const dialog = reactive({ visible: false, title: '', isEdit: false })
const form = reactive({ 
  id: undefined, 
  username: '', 
  password: '', 
  phone: '', 
  dept_id: null, 
  role_id: null, 
  post: '', 
  status: 1 
})
const formRef = ref()

const rules = { 
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }] 
}

const getList = async () => {
  loading.value = true
  try {
    const res: any = await getUserList(queryParams)
    tableData.value = res
  } finally {
    loading.value = false
  }
}

const loadOpts = async () => {
    try {
      deptList.value = await getDeptList() as any
      roleList.value = await getRoleList() as any
    } catch(e) {}
}

const handleAdd = () => {
  dialog.title = '新增用户'
  dialog.isEdit = false
  dialog.visible = true
  form.id = undefined
  form.username = ''
  form.password = ''
  form.phone = ''
  form.dept_id = null
  form.role_id = null
  form.post = ''
  form.status = 1
}

const handleEdit = (row: any) => {
  dialog.title = '修改用户'
  dialog.isEdit = true
  dialog.visible = true
  Object.assign(form, row)
  form.password = '' 
}

const submitForm = async () => {
  await formRef.value.validate(async (valid: boolean) => {
    if(valid) {
        if(dialog.isEdit) await updateUser(form.id!, form)
        else await createUser(form)
        ElMessage.success('操作成功')
        dialog.visible = false
        getList()
    }
  })
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该用户?', '警告', { 
    confirmButtonText: '确定', 
    cancelButtonText: '取消', 
    type: 'warning' 
  }).then(async () => {
    await deleteUser(row.id)
    ElMessage.success('已删除')
    getList()
  })
}

const handleStatus = async (row: any) => {
    try {
      await updateUserStatus(row.id, row.status)
      ElMessage.success('状态更新成功')
    } catch (error) {
      row.status = row.status === 1 ? 0 : 1
    }
}

const handleResetPwd = (row: any) => {
    ElMessageBox.prompt('请输入新密码', '重置密码', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'password',
        inputPattern: /.{6,}/,
        inputErrorMessage: '密码长度至少6位'
    }).then(async ({ value }) => {
        await resetUserPassword(row.id, { new_password: value })
        ElMessage.success('密码重置成功')
    }).catch(() => {})
}

const handleImport = async (options: any) => {
    try {
      const res: any = await importUsers(options.file)
      ElMessage.success(`成功导入 ${res.success} 条`)
      getList()
    } catch (error) {
      ElMessage.error('导入失败')
    }
}

onMounted(() => { 
  getList()
  loadOpts() 
})
</script>
<style scoped>.card-header { display: flex; justify-content: space-between; }</style>