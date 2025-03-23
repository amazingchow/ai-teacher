<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold">题库管理</h1>
      <Button label="添加题目" icon="pi pi-plus" @click="openNewDialog" />
    </div>

    <DataTable
      :value="questions"
      :paginator="true"
      :rows="10"
      :loading="loading"
      stripedRows
      class="p-datatable-sm"
    >
      <Column field="category" header="分类" sortable></Column>
      <Column field="title" header="题目标题" sortable>{{ data.title }}</Column>
      <Column field="content" header="题目内容" sortable>
        <template #body="{ data }">
          <div class="truncate max-w-[300px] cursor-pointer hover:text-primary" @click="showFullText(data.content)">
            {{ data.content }}
          </div>
        </template>
      </Column>
      <Column field="answer" header="答案" sortable></Column>
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
      :header="dialogMode === 'create' ? '添加题目' : '编辑题目'"
      class="w-[600px]"
    >
      <div class="flex flex-col gap-4">
        <div class="field">
          <label for="category" class="block mb-2">分类</label>
          <Dropdown
            id="category"
            v-model="question.category"
            :options="categoryOptions"
            class="w-full"
            :class="{ 'p-invalid': v$.category.$invalid && submitted }"
          />
          <small v-if="v$.category.$invalid && submitted" class="p-error">
            {{ v$.category.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="title" class="block mb-2">题目标题</label>
          <Textarea
            id="title"
            v-model="question.title"
            rows="2"
            class="w-full"
            :class="{ 'p-invalid': v$.title.$invalid && submitted }"
          />
          <small v-if="v$.title.$invalid && submitted" class="p-error">
            {{ v$.title.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="content" class="block mb-2">题目内容</label>
          <Textarea
            id="content"
            v-model="question.content"
            rows="4"
            class="w-full"
            :class="{ 'p-invalid': v$.content.$invalid && submitted }"
          />
          <small v-if="v$.content.$invalid && submitted" class="p-error">
            {{ v$.content.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="answer" class="block mb-2">答案</label>
          <Textarea
            id="answer"
            v-model="question.answer"
            rows="3"
            class="w-full"
            :class="{ 'p-invalid': v$.answer.$invalid && submitted }"
          />
          <small v-if="v$.answer.$invalid && submitted" class="p-error">
            {{ v$.answer.$errors[0].$message }}
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
            @click="saveQuestion"
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
        确定要删除这道题目吗？此操作不可撤销。
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
            @click="deleteQuestion"
            :loading="deleting"
          />
        </div>
      </template>
    </Dialog>
    <!-- 添加全文显示对话框 -->
    <Dialog
      v-model:visible="fullTextDialogVisible"
      :modal="true"
      header="完整内容"
      class="w-[600px]"
    >
      <p class="whitespace-pre-wrap">{{ fullText }}</p>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, minLength } from '@vuelidate/validators'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'

// 组件
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'

const toast = useToast()

// 数据
const questions = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('create')
const deleteDialogVisible = ref(false)
const saving = ref(false)
const deleting = ref(false)
const submitted = ref(false)
const selectedQuestion = ref(null)

const question = reactive({
  id: null,
  category: '',
  title: '',
  content: '',
  answer: ''
})

const categoryOptions = [
  '课本背诵',
]

// 表单验证规则
const rules = computed(() => ({
  category: { required },
  title: { required, minLength: minLength(2) },
  content: { required, minLength: minLength(2) },
  answer: { minLength: minLength(2) }
}))

const v$ = useVuelidate(rules, question)

// 方法
const loadQuestions = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/questions')
    questions.value = response.data.map(q => ({
      ...q,
      answer: q.answer || ''
    }))
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: '错误',
      detail: '加载题目列表失败',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const openNewDialog = () => {
  dialogMode.value = 'create'
  Object.assign(question, {
    id: null,
    category: '',
    title: '',
    answer: ''
  })
  submitted.value = false
  dialogVisible.value = true
}

const openEditDialog = (data) => {
  dialogMode.value = 'edit'
  Object.assign(question, { ...data })
  submitted.value = false
  dialogVisible.value = true
}

const hideDialog = () => {
  dialogVisible.value = false
  submitted.value = false
}

const saveQuestion = async () => {
  submitted.value = true
  const isValid = await v$.value.$validate()
  if (!isValid) return

  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      await axios.post('/api/questions', question)
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '添加题目成功',
        life: 3000
      })
    } else {
      await axios.put(`/api/questions/${question.id}`, question)
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '更新题目成功',
        life: 3000
      })
    }
    hideDialog()
    await loadQuestions()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: '错误',
      detail: dialogMode.value === 'create' ? '添加题目失败' : '更新题目失败',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

const confirmDelete = (data) => {
  selectedQuestion.value = data
  deleteDialogVisible.value = true
}

const deleteQuestion = async () => {
  if (!selectedQuestion.value) return

  deleting.value = true
  try {
    await axios.delete(`/api/questions/${selectedQuestion.value.id}`)
    deleteDialogVisible.value = false
    toast.add({
      severity: 'success',
      summary: '成功',
      detail: '删除题目成功',
      life: 3000
    })
    await loadQuestions()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: '错误',
      detail: '删除题目失败',
      life: 3000
    })
  } finally {
    deleting.value = false
  }
}

// 初始化加载数据
loadQuestions()

// 在 script setup 部分添加
const fullTextDialogVisible = ref(false)
const fullText = ref('')

const showFullText = (text) => {
  fullText.value = text
  fullTextDialogVisible.value = true
}
</script>