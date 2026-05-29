<template>
  <div class="migration-step-form">
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑迁徙记录' : '新增迁徙记录'"
      width="900px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-steps :active="currentStep" finish-status="success" class="form-steps">
        <el-step title="基本信息" description="迁徙时间与地点" />
        <el-step title="详细描述" description="迁徙背景与经历" />
        <el-step title="证据上传" description="族谱与影像资料" />
      </el-steps>

      <div class="form-content">
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-width="100px"
          class="migration-form"
        >
          <div v-show="currentStep === 0" class="step-content">
            <el-form-item label="所属分支" prop="branch_id">
              <el-select
                v-model="formData.branch_id"
                placeholder="请选择所属分支"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="branch in branches"
                  :key="branch.branch_id"
                  :label="branch.branch_name"
                  :value="branch.branch_id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="迁徙时期" prop="migration_period">
              <el-input
                v-model="formData.migration_period"
                placeholder="如：明洪武年间、清康熙年间、1990年代"
              >
                <template #append>
                  <el-dropdown @command="handleEraSelect" trigger="click">
                    <el-button>快速选择</el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="ming_hongwu">明洪武年间</el-dropdown-item>
                        <el-dropdown-item command="ming_yongle">明永乐年间</el-dropdown-item>
                        <el-dropdown-item command="qing_kangxi">清康熙年间</el-dropdown-item>
                        <el-dropdown-item command="qing_qianlong">清乾隆年间</el-dropdown-item>
                        <el-dropdown-item command="qing_mo_min">清末民初</el-dropdown-item>
                        <el-dropdown-item command="minguo">民国时期</el-dropdown-item>
                        <el-dropdown-item command="jianguo_early">建国初期</el-dropdown-item>
                        <el-dropdown-item command="reform_open">改革开放后</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="估计年份" prop="estimated_year">
              <el-input-number
                v-model="formData.estimated_year"
                :min="1000"
                :max="2100"
                placeholder="如：1368"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="迁出地" prop="from_location">
              <div class="location-picker-wrapper">
                <LocationPicker
                  :longitude="formData.from_longitude"
                  :latitude="formData.from_latitude"
                  :address="formData.from_address"
                  @confirm="handleFromLocationConfirm"
                />
                <div v-if="formData.from_longitude" class="location-coords">
                  坐标: {{ formData.from_longitude?.toFixed(6) }}, {{ formData.from_latitude?.toFixed(6) }}
                </div>
              </div>
            </el-form-item>

            <el-form-item label="迁入地" prop="to_location">
              <div class="location-picker-wrapper">
                <LocationPicker
                  :longitude="formData.to_longitude"
                  :latitude="formData.to_latitude"
                  :address="formData.to_address"
                  @confirm="handleToLocationConfirm"
                />
                <div v-if="formData.to_longitude" class="location-coords">
                  坐标: {{ formData.to_longitude?.toFixed(6) }}, {{ formData.to_latitude?.toFixed(6) }}
                </div>
              </div>
            </el-form-item>

            <el-form-item label="迁徙原因" prop="reason">
              <el-select
                v-model="formData.reason"
                placeholder="请选择迁徙原因"
                allow-create
                filterable
                default-first-option
                style="width: 100%"
              >
                <el-option label="战乱避难" value="战乱避难" />
                <el-option label="经商移民" value="经商移民" />
                <el-option label="官员调任" value="官员调任" />
                <el-option label="自然灾害" value="自然灾害" />
                <el-option label="人口迁移" value="人口迁移" />
                <el-option label="婚嫁迁徙" value="婚嫁迁徙" />
                <el-option label="寻根问祖" value="寻根问祖" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </div>

          <div v-show="currentStep === 1" class="step-content">
            <el-form-item label="关键人物" prop="key_figure">
              <el-input
                v-model="formData.key_figure"
                placeholder="如：张三（族长）、李四（商人）"
              />
            </el-form-item>

            <el-form-item label="详细描述" prop="description">
              <div class="editor-wrapper">
                <Toolbar
                  :editor="editorRef"
                  :defaultConfig="toolbarConfig"
                  mode="default"
                />
                <Editor
                  ref="editorRef"
                  v-model="formData.description"
                  :defaultConfig="editorConfig"
                  mode="default"
                  @onCreated="handleEditorCreated"
                />
              </div>
            </el-form-item>

            <el-form-item label="老照片">
              <el-upload
                v-model:file-list="formData.old_photos"
                action="/api/upload"
                list-type="picture-card"
                :on-preview="handlePictureCardPreview"
                :on-remove="handleOldPhotoRemove"
                :before-upload="beforePhotoUpload"
                :http-request="uploadPhoto"
                multiple
                accept="image/*"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="upload-hint">支持拖拽上传，单个文件不超过5MB</div>
            </el-form-item>
          </div>

          <div v-show="currentStep === 2" class="step-content">
            <el-form-item label="族谱照片">
              <el-upload
                v-model:file-list="formData.genealogy_photos"
                action="/api/upload"
                list-type="picture-card"
                :on-preview="handlePictureCardPreview"
                :on-remove="handleGenealogyPhotoRemove"
                :before-upload="beforePhotoUpload"
                :http-request="uploadPhoto"
                multiple
                accept="image/*"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="upload-hint">支持多图上传，可查看缩略图</div>
            </el-form-item>

            <el-form-item label="音频文件">
              <el-upload
                v-model:file-list="formData.audio_files"
                :before-upload="beforeAudioUpload"
                :http-request="uploadChunked"
                :on-remove="handleAudioRemove"
                :on-change="handleAudioChange"
                multiple
                accept="audio/*"
              >
                <el-button type="primary" plain><el-icon><Microphone /></el-icon> 上传音频</el-button>
              </el-upload>
              <div v-if="uploadingAudio" class="upload-progress">
                <el-progress
                  :percentage="audioUploadProgress"
                  :status="audioUploadStatus"
                />
                <span class="progress-text">{{ uploadingAudioName }}</span>
              </div>
            </el-form-item>

            <el-form-item label="视频文件">
              <el-upload
                v-model:file-list="formData.video_files"
                :before-upload="beforeVideoUpload"
                :http-request="uploadChunked"
                :on-remove="handleVideoRemove"
                :on-change="handleVideoChange"
                multiple
                accept="video/*"
              >
                <el-button type="primary" plain><el-icon><VideoCamera /></el-icon> 上传视频</el-button>
              </el-upload>
              <div v-if="uploadingVideo" class="upload-progress">
                <el-progress
                  :percentage="videoUploadProgress"
                  :status="videoUploadStatus"
                />
                <span class="progress-text">{{ uploadingVideoName }}</span>
              </div>
            </el-form-item>

            <el-form-item label="补充说明">
              <el-input
                v-model="formData.reason_detail"
                type="textarea"
                :rows="3"
                placeholder="其他补充说明或口述内容概要"
              />
            </el-form-item>
          </div>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCancel">取消</el-button>
          <el-button v-if="currentStep > 0" @click="handlePrev">上一步</el-button>
          <el-button v-if="currentStep < 2" type="primary" @click="handleNext">下一步</el-button>
          <el-button v-else type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '提交记录' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-image-viewer
      v-if="previewVisible"
      :url-list="[previewImage]"
      @close="previewVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, provide, inject } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Microphone, VideoCamera } from '@element-plus/icons-vue'
import axios from 'axios'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import LocationPicker from './LocationPicker.vue'
import { fetchBranches, fetchLocations } from '@/api/genealogy'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  migrationData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.migrationData?.migration_id)

const currentStep = ref(0)
const submitting = ref(false)
const formRef = ref(null)
const editorRef = ref(null)

const branches = ref([])
const locations = ref([])

const formData = reactive({
  branch_id: null,
  migration_period: '',
  estimated_year: null,
  from_location_id: null,
  from_longitude: null,
  from_latitude: null,
  from_address: '',
  to_location_id: null,
  to_longitude: null,
  to_latitude: null,
  to_address: '',
  reason: '',
  key_figure: '',
  description: '',
  reason_detail: '',
  old_photos: [],
  genealogy_photos: [],
  audio_files: [],
  video_files: []
})

const CHUNK_SIZE = 2 * 1024 * 1024
const uploadingAudio = ref(false)
const uploadingVideo = ref(false)
const audioUploadProgress = ref(0)
const videoUploadProgress = ref(0)
const audioUploadStatus = ref('')
const videoUploadStatus = ref('')
const uploadingAudioName = ref('')
const uploadingVideoName = ref('')

const previewVisible = ref(false)
const previewImage = ref('')

const formRules = {
  branch_id: [{ required: true, message: '请选择所属分支', trigger: 'change' }],
  migration_period: [{ required: true, message: '请输入迁徙时期', trigger: 'blur' }],
  from_location: [{ required: true, validator: validateFromLocation, trigger: 'change' }],
  to_location: [{ required: true, validator: validateToLocation, trigger: 'change' }],
  reason: [{ required: true, message: '请选择迁徙原因', trigger: 'change' }]
}

function validateFromLocation(rule, value, callback) {
  if (!formData.from_longitude) {
    callback(new Error('请选择迁出地'))
  } else {
    callback()
  }
}

function validateToLocation(rule, value, callback) {
  if (!formData.to_longitude) {
    callback(new Error('请选择迁入地'))
  } else {
    callback()
  }
}

const toolbarConfig = {
  excludeKeys: ['group-video']
}

const editorConfig = {
  placeholder: '请详细描述迁徙的背景、经过和影响...',
  MENU_CONF: {
    uploadImage: {
      server: '/api/upload',
      maxFileSize: 5 * 1024 * 1024,
      fieldName: 'file'
    }
  }
}

let editorInstance = null

const handleEditorCreated = (editor) => {
  editorInstance = editor
}

const eraMap = {
  ming_hongwu: '明洪武年间',
  ming_yongle: '明永乐年间',
  qing_kangxi: '清康熙年间',
  qing_qianlong: '清乾隆年间',
  qing_mo_min: '清末民初',
  minguo: '民国时期',
  jianguo_early: '建国初期',
  reform_open: '改革开放后'
}

const handleEraSelect = (command) => {
  formData.migration_period = eraMap[command] || command
}

const handleFromLocationConfirm = (data) => {
  formData.from_longitude = data.longitude
  formData.from_latitude = data.latitude
  formData.from_address = data.address
  formRef.value?.validateField('from_location')
}

const handleToLocationConfirm = (data) => {
  formData.to_longitude = data.longitude
  formData.to_latitude = data.latitude
  formData.to_address = data.address
  formRef.value?.validateField('to_location')
}

const handlePictureCardPreview = (uploadFile) => {
  previewImage.value = uploadFile.url
  previewVisible.value = true
}

const handleOldPhotoRemove = (file, fileList) => {
  formData.old_photos = fileList
}

const handleGenealogyPhotoRemove = (file, fileList) => {
  formData.genealogy_photos = fileList
}

const handleAudioRemove = (file, fileList) => {
  formData.audio_files = fileList
}

const handleVideoRemove = (file, fileList) => {
  formData.video_files = fileList
}

const handleAudioChange = (file, fileList) => {
  if (file.status === 'uploading') {
    uploadingAudioName.value = file.name
  }
}

const handleVideoChange = (file, fileList) => {
  if (file.status === 'uploading') {
    uploadingVideoName.value = file.name
  }
}

const beforePhotoUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const beforeAudioUpload = (file) => {
  const isAudio = file.type.startsWith('audio/')
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isAudio) {
    ElMessage.error('只能上传音频文件!')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('音频大小不能超过 50MB!')
    return false
  }
  uploadingAudio.value = true
  uploadingAudioName.value = file.name
  return true
}

const beforeVideoUpload = (file) => {
  const isVideo = file.type.startsWith('video/')
  const isLt200M = file.size / 1024 / 1024 < 200

  if (!isVideo) {
    ElMessage.error('只能上传视频文件!')
    return false
  }
  if (!isLt200M) {
    ElMessage.error('视频大小不能超过 200MB!')
    return false
  }
  uploadingVideo.value = true
  uploadingVideoName.value = file.name
  return true
}

const uploadPhoto = async (options) => {
  const { file, onSuccess, onError, onProgress } = options
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await axios.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        onProgress({ percent: Math.round((e.loaded / e.total) * 100) })
      }
    })
    onSuccess(response.data)
    ElMessage.success('上传成功')
  } catch (error) {
    onError(error)
    ElMessage.error('上传失败')
  }
}

const uploadChunked = async (options) => {
  const { file, onSuccess, onError, onProgress } = options
  const isAudio = file.type.startsWith('audio/')
  const progressRef = isAudio ? audioUploadProgress : videoUploadProgress
  const statusRef = isAudio ? audioUploadStatus : videoUploadStatus

  const totalChunks = Math.ceil(file.size / CHUNK_SIZE)
  const fileHash = await calculateFileHash(file)
  const fileId = `${fileHash}_${file.name}`

  progressRef.value = 0
  statusRef.value = ''

  try {
    for (let i = 0; i < totalChunks; i++) {
      const start = i * CHUNK_SIZE
      const end = Math.min(start + CHUNK_SIZE, file.size)
      const chunk = file.slice(start, end)

      const formData = new FormData()
      formData.append('file', chunk)
      formData.append('fileName', file.name)
      formData.append('fileId', fileId)
      formData.append('chunkIndex', i.toString())
      formData.append('totalChunks', totalChunks.toString())

      await axios.post('/api/upload/chunked', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      progressRef.value = Math.round(((i + 1) / totalChunks) * 100)
    }

    const response = await axios.post('/api/upload/merge', {
      fileId,
      fileName: file.name,
      totalChunks
    })

    if (isAudio) {
      uploadingAudio.value = false
      formData.audio_files.push({
        name: file.name,
        url: response.data.url,
        status: 'success'
      })
    } else {
      uploadingVideo.value = false
      formData.video_files.push({
        name: file.name,
        url: response.data.url,
        status: 'success'
      })
    }

    statusRef.value = 'success'
    onSuccess(response.data)
    ElMessage.success('上传成功')
  } catch (error) {
    statusRef.value = 'exception'
    if (isAudio) {
      uploadingAudio.value = false
    } else {
      uploadingVideo.value = false
    }
    onError(error)
    ElMessage.error('上传失败')
  }
}

async function calculateFileHash(file) {
  const buffer = await file.arrayBuffer()
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

const handleNext = async () => {
  if (currentStep.value === 0) {
    try {
      await formRef.value?.validate()
      currentStep.value++
    } catch {
      return
    }
  } else if (currentStep.value === 1) {
    currentStep.value++
  }
}

const handlePrev = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    const submitData = {
      branch_id: formData.branch_id,
      from_location_id: formData.from_location_id,
      to_location_id: formData.to_location_id,
      migration_period: formData.migration_period,
      estimated_year: formData.estimated_year,
      reason: formData.reason,
      reason_detail: formData.reason_detail,
      key_figure: formData.key_figure,
      description: formData.description,
      route_points: JSON.stringify({
        from: [formData.from_longitude, formData.from_latitude],
        to: [formData.to_longitude, formData.to_latitude]
      }),
      old_photo_urls: formData.old_photos.map(f => f.url || f.response?.url).filter(Boolean),
      genealogy_photo_urls: formData.genealogy_photos.map(f => f.url || f.response?.url).filter(Boolean),
      audio_urls: formData.audio_files.map(f => f.url || f.response?.url).filter(Boolean),
      video_urls: formData.video_files.map(f => f.url || f.response?.url).filter(Boolean)
    }

    if (props.migrationData?.migration_id) {
      await axios.put(`/api/migrations/${props.migrationData.migration_id}`, submitData)
      ElMessage.success('迁徙记录更新成功')
    } else {
      await axios.post('/api/migrations', submitData)
      ElMessage.success('迁徙记录创建成功')
    }

    dialogVisible.value = false
    emit('success')
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || '保存失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleCancel = async () => {
  if (currentStep.value > 0 || formData.description) {
    try {
      await ElMessageBox.confirm('确定要取消吗？未保存的内容将丢失', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '继续填写',
        type: 'warning'
      })
      dialogVisible.value = false
    } catch {
      return
    }
  } else {
    dialogVisible.value = false
  }
}

const resetForm = () => {
  Object.assign(formData, {
    branch_id: null,
    migration_period: '',
    estimated_year: null,
    from_location_id: null,
    from_longitude: null,
    from_latitude: null,
    from_address: '',
    to_location_id: null,
    to_longitude: null,
    to_latitude: null,
    to_address: '',
    reason: '',
    key_figure: '',
    description: '',
    reason_detail: '',
    old_photos: [],
    genealogy_photos: [],
    audio_files: [],
    video_files: []
  })
  currentStep.value = 0
  if (editorInstance) {
    editorInstance.setHtml('')
  }
}

const loadBranches = async () => {
  try {
    branches.value = await fetchBranches()
  } catch (error) {
    console.error('加载分支失败:', error)
  }
}

const loadLocations = async () => {
  try {
    locations.value = await fetchLocations()
  } catch (error) {
    console.error('加载地点失败:', error)
  }
}

watch(dialogVisible, async (val) => {
  if (val) {
    await loadBranches()
    await loadLocations()

    if (props.migrationData?.migration_id) {
      Object.assign(formData, {
        branch_id: props.migrationData.branch_id,
        migration_period: props.migrationData.migration_period || props.migrationData.period,
        estimated_year: props.migrationData.estimated_year,
        from_location_id: props.migrationData.from_location_id,
        to_location_id: props.migrationData.to_location_id,
        reason: props.migrationData.reason,
        key_figure: props.migrationData.key_figure,
        description: props.migrationData.description || '',
        reason_detail: props.migrationData.reason_detail || ''
      })

      if (props.migrationData.from_longitude) {
        formData.from_longitude = props.migrationData.from_longitude
        formData.from_latitude = props.migrationData.from_latitude
        formData.from_address = props.migrationData.from_name || ''
      }

      if (props.migrationData.to_longitude) {
        formData.to_longitude = props.migrationData.to_longitude
        formData.to_latitude = props.migrationData.to_latitude
        formData.to_address = props.migrationData.to_name || ''
      }
    } else {
      resetForm()
    }
  }
})

provide('formData', formData)

defineExpose({
  resetForm
})
</script>

<style scoped>
.migration-step-form {
  width: 100%;
}

.form-steps {
  margin-bottom: 30px;
  padding: 0 20px;
}

.form-content {
  max-height: 60vh;
  overflow-y: auto;
  padding: 10px 20px;
}

.step-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.location-picker-wrapper {
  width: 100%;
}

.location-coords {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

.editor-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-wrapper :deep(.w-e-toolbar) {
  border-bottom: 1px solid #dcdfe6;
}

.editor-wrapper :deep(.w-e-text-container) {
  height: 200px !important;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.upload-progress {
  margin-top: 10px;
}

.upload-progress .progress-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  display: block;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-upload-list--picture-card) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
