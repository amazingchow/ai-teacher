<template>
  <div class="p-4">
    <div class="mb-6 bg-white rounded-lg shadow p-4">
      <h2 class="text-xl font-bold mb-4">课本背诵</h2>

      <!-- 题目选择 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">选择题目</label>
        <Dropdown
          v-model="selectedQuestion"
          :options="questions"
          optionLabel="title"
          placeholder="请选择题目"
          class="w-full"
        />
      </div>

      <!-- 学生选择 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">选择学生</label>
        <Dropdown
          v-model="selectedStudent"
          :options="students"
          optionLabel="name"
          placeholder="请选择学生"
          class="w-full"
        />
      </div>

      <!-- 录音控制 -->
      <div class="flex justify-center space-x-4">
        <Button
          :label="isRecording ? '结束背诵' : '开始背诵'"
          :class="isRecording ? 'p-button-danger' : 'p-button-success'"
          @click="toggleRecording"
          :disabled="!selectedStudent || !selectedQuestion"
        />
        <Button
          label="重新开始"
          class="p-button-secondary"
          @click="resetRecording"
          :disabled="!recordingComplete"
        />
        <Button
          label="批量检查"
          class="p-button-info"
          @click="batchCheck"
          :disabled="!hasRecordings"
        />
      </div>
    </div>

    <!-- 已录制学生列表 -->
    <div class="bg-white rounded-lg shadow p-4">
      <h3 class="text-lg font-semibold mb-3">已录制学生</h3>
      <div class="space-y-2">
        <div v-for="recording in recordings" :key="recording.id" class="p-3 bg-gray-50 rounded">
          <div class="flex justify-between items-center">
            <div>
              <span class="font-medium">{{ recording.studentName }}</span>
              <span class="text-gray-500 text-sm ml-2">({{ recording.duration }}秒)</span>
              <span v-if="recording.check_result === 'checked'" class="ml-2 text-blue-600">
                得分: {{ recording.score }}
              </span>
            </div>
            <span :class="['px-2 py-1 rounded text-sm', recording.check_result === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800']">
              {{ recording.check_result === 'checked' ? '已检查' : '待检查' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'

// 存储学生和题目数据
const students = ref([])
const questions = ref([])

// 获取学生列表
async function fetchStudents() {
  try {
    const response = await fetch('/api/students')
    if (response.ok) {
      students.value = await response.json()
    }
  } catch (error) {
    console.error('获取学生列表失败:', error)
  }
}

// 获取题目列表
async function fetchQuestions() {
  try {
    const response = await fetch('/api/questions')
    if (response.ok) {
      questions.value = await response.json()
    }
  } catch (error) {
    console.error('获取题目列表失败:', error)
  }
}

// 在组件加载时获取数据
fetchStudents()
fetchQuestions()

const selectedStudent = ref(null)
const selectedQuestion = ref(null)
const isRecording = ref(false)
const recordingComplete = ref(false)
const recordings = ref([])
const mediaRecorder = ref(null)
const audioChunks = ref([])
const pollingInterval = ref(null) // 用于存储轮询定时器

const hasRecordings = computed(() => 
  selectedQuestion.value?.id && recordings.value.length > 0
)

// 检查是否所有录音都已完成检查
const allRecordingsChecked = computed(() => 
  recordings.value.length > 0 && recordings.value.every(recording => recording.check_result === 'checked')
)

// 添加 watch 来监听选中题目的变化
watch(selectedQuestion, async (newQuestion) => {
  if (newQuestion?.id) {
    await fetchRecordedStudents(newQuestion.id)
  } else {
    recordings.value = []
  }
})

// 获取已录制学生列表
async function fetchRecordedStudents(questionId) {
  try {
    const response = await fetch(`/api/recordings/${questionId}`)
    if (response.ok) {
      const data = await response.json()
      recordings.value = data.map(recording => ({
        id: recording.id,
        studentName: recording.student_name,
        duration: recording.duration,
        check_result: recording.check_result || 'pending',
        score: recording.score
      }))
    }
  } catch (error) {
    console.error('获取已录制学生列表失败:', error)
  }
}

// 开始/结束录音
async function toggleRecording() {
  if (!isRecording.value) {
    // 检查学生和题目是否已选择
    if (!selectedStudent.value || !selectedQuestion.value) {
      console.error('请先选择学生和题目')
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder.value = new MediaRecorder(stream)
      audioChunks.value = []

      mediaRecorder.value.ondataavailable = (event) => {
        audioChunks.value.push(event.data)
      }

      let startTime = 0

      mediaRecorder.value.onstart = () => {
        startTime = Date.now()
      }

      mediaRecorder.value.onstop = async () => {
        // 计算录音时长（秒）
        const duration = (Date.now() - startTime) / 1000
        
        // 检查学生和题目信息是否完整
        if (!selectedStudent.value?.student_id || !selectedQuestion.value?.id) {
          console.log(selectedStudent)
          console.error('学生或题目信息不完整')
          return
        }
        
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
        const fileName = `${selectedQuestion.value.id}_${selectedStudent.value.student_id}_${new Date().toISOString().split('T')[0]}.webm`
        
        // 创建FormData对象
        const formData = new FormData()
        formData.append('audio', audioBlob, fileName)
        formData.append('student_id', selectedStudent.value.student_id)
        formData.append('question_id', selectedQuestion.value.id)
        formData.append('duration', duration.toString())

        try {
          // 上传录音文件
          const response = await fetch('/api/recordings', {
            method: 'POST',
            body: formData
          })

          if (response.ok) {
            const data = await response.json()
            recordings.value.push({
              id: Date.now(),
              studentName: selectedStudent.value.name,
              duration: data.duration,
              check_result: 'pending',
              score: null
            })
            recordingComplete.value = true
          }
        } catch (error) {
          console.error('上传失败:', error)
        }
      }

      mediaRecorder.value.start()
      isRecording.value = true
    } catch (error) {
      console.error('无法访问麦克风:', error)
    }
  } else {
    mediaRecorder.value.stop()
    mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
    isRecording.value = false
  }
}

// 重置录音
function resetRecording() {
  selectedStudent.value = null
  selectedQuestion.value = null
  recordingComplete.value = false
}

// 批量检查录音
async function batchCheck() {
  try {
    const response = await fetch(`/api/recordings/batch-check/${selectedQuestion.value?.id}`)

    if (response.ok) {
      // 开始轮询检查状态
      startPolling()
    }
  } catch (error) {
    console.error('检查失败:', error)
  }
}

// 开始轮询
function startPolling() {
  // 清除可能存在的之前的轮询
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }

  // 设置新的轮询
  pollingInterval.value = setInterval(async () => {
    await fetchRecordedStudents(selectedQuestion.value?.id)
    
    // 如果所有录音都已检查完成，停止轮询
    if (allRecordingsChecked.value) {
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
  }, 5000) // 每5秒轮询一次
}

// 在组件卸载时清除轮询
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
})
</script>