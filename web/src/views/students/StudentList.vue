<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold">学生管理</h1>
      <Button label="添加学生" icon="pi pi-plus" @click="openNewDialog" />
    </div>

    <DataTable
      :value="students"
      :paginator="true"
      :rows="10"
      :loading="loading"
      stripedRows
      class="p-datatable-sm"
    >
      <Column field="student_id" header="学号" sortable></Column>
      <Column field="name" header="姓名" sortable></Column>
      <Column field="gender" header="性别" sortable>
        <template #body="{ data }">
          {{ data.gender === 'M' ? '男' : '女' }}
        </template>
      </Column>
      <Column field="age" header="年龄" sortable></Column>
      <Column field="class_name" header="班级" sortable></Column>
      <Column header="操作">
        <template #body="{ data }">
          <div class="flex gap-2">
            <Button
              icon="pi pi-pencil"
              severity="secondary"
              text
              rounded
              @click="openEditDialog(data)"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              @click="confirmDelete(data)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- 添加/编辑对话框 -->
    <Dialog
      v-model:visible="dialogVisible"
      :modal="true"
      :header="dialogMode === 'create' ? '添加学生' : '编辑学生'"
      class="w-[500px]"
    >
      <div class="flex flex-col gap-4">
        <div class="field">
          <label for="name" class="block mb-2">姓名</label>
          <InputText
            id="name"
            v-model="student.name"
            class="w-full"
            :class="{ 'p-invalid': v$.name.$invalid && submitted }"
          />
          <small v-if="v$.name.$invalid && submitted" class="p-error">
            {{ v$.name.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="student_id" class="block mb-2">学号</label>
          <InputText
            id="student_id"
            v-model="student.student_id"
            class="w-full"
            :class="{ 'p-invalid': v$.student_id.$invalid && submitted }"
          />
          <small v-if="v$.student_id.$invalid && submitted" class="p-error">
            {{ v$.student_id.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="gender" class="block mb-2">性别</label>
          <Dropdown
            id="gender"
            v-model="student.gender"
            :options="genderOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
            :class="{ 'p-invalid': v$.gender.$invalid && submitted }"
          />
          <small v-if="v$.gender.$invalid && submitted" class="p-error">
            {{ v$.gender.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="age" class="block mb-2">年龄</label>
          <InputNumber
            id="age"
            v-model="student.age"
            class="w-full"
            :min="6"
            :max="15"
            :class="{ 'p-invalid': v$.age.$invalid && submitted }"
          />
          <small v-if="v$.age.$invalid && submitted" class="p-error">
            {{ v$.age.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="class_name" class="block mb-2">班级</label>
          <InputText
            id="class_name"
            v-model="student.class_name"
            class="w-full"
            :class="{ 'p-invalid': v$.class_name.$invalid && submitted }"
          />
          <small v-if="v$.class_name.$invalid && submitted" class="p-error">
            {{ v$.class_name.$errors[0].$message }}
          </small>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button
            label="取消"
            icon="pi pi-times"
            @click="hideDialog"
            text
          />
          <Button
            label="保存"
            icon="pi pi-check"
            @click="saveStudent"
            :loading="saving"
          />
        </div>
      </template>
    </Dialog>

    <!-- 删除确认对话框 -->
    <Dialog
      v-model:visible="deleteDialogVisible"
      :modal="true"
      header="确认删除"
      class="w-[400px]"
    >
      <div class="mb-4">
        确定要删除学生 <strong>{{ selectedStudent?.name }}</strong> 吗？此操作不可撤销。
      </div>
      <template #footer>
        <div class="flex justify-end gap-2">
          <Button
            label="取消"
            icon="pi pi-times"
            @click="deleteDialogVisible = false"
            text
          />
          <Button
            label="删除"
            icon="pi pi-trash"
            severity="danger"
            @click="deleteStudent"
            :loading="deleting"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, minLength, maxLength, numeric, between } from '@vuelidate/validators'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'

// 组件
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'

const toast = useToast()

// 数据
const students = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('create')
const deleteDialogVisible = ref(false)
const saving = ref(false)
const deleting = ref(false)
const submitted = ref(false)
const selectedStudent = ref(null)

const student = reactive({
  id: null,
  name: '',
  student_id: '',
  gender: null,
  age: null,
  class_name: ''
})

const genderOptions = [
  { label: '男', value: 'M' },
  { label: '女', value: 'F' }
]

// 表单验证规则
const rules = computed(() => ({
  name: { required, minLength: minLength(2), maxLength: maxLength(20) },
  student_id: { required, minLength: minLength(2), maxLength: maxLength(20) },
  gender: { required },
  age: { required, between: between(6, 15) },
  class_name: { required, minLength: minLength(2), maxLength: maxLength(20) }
}))

const v$ = useVuelidate(rules, student)

// 方法
const loadStudents = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/students')
    students.value = response.data
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: '错误',
      detail: '加载学生列表失败',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const openNewDialog = () => {
  dialogMode.value = 'create'
  Object.assign(student, {
    id: null,
    name: '',
    student_id: '',
    gender: null,
    age: null,
    class_name: ''
  })
  submitted.value = false
  dialogVisible.value = true
}

const openEditDialog = (data) => {
  dialogMode.value = 'edit'
  Object.assign(student, { ...data })
  submitted.value = false
  dialogVisible.value = true
}

const hideDialog = () => {
  dialogVisible.value = false
  submitted.value = false
}

const saveStudent = async () => {
  submitted.value = true
  const isValid = await v$.value.$validate()
  if (!isValid) return

  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      await axios.post('/api/students', student)
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '添加学生成功',
        life: 3000
      })
    } else {
      await axios.put(`/api/students/${student.id}`, student)
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '更新学生成功',
        life: 3000
      })
    }
    hideDialog()
    await loadStudents()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: '错误',
      detail: dialogMode.value === 'create' ? '添加学生失败' : '更新学生失败',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

const confirmDelete = (data) => {
  selectedStudent.value = data
  deleteDialogVisible.value = true
}

const deleteStudent = async () => {
  if (!selectedStudent.value) return

  deleting.value = true
  try {
    await axios.delete(`/api/students/${selectedStudent.value.id}`)
    deleteDialogVisible.value = false
    toast.add({
      severity: 'success',
      summary: '成功',
      detail: '删除学生成功',
      life: 3000
    })
    await loadStudents()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: '错误',
      detail: '删除学生失败',
      life: 3000
    })
  } finally {
    deleting.value = false
  }
}

// 初始化加载数据
loadStudents()
</script>