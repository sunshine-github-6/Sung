<template>
  <div class="common-filter">
    <el-row :gutter="20">
      <el-col
        v-for="filter in filters"
        :key="filter.key"
        :span="filter.span || 6"
      >
        <el-input
          v-if="filter.type === 'input'"
          v-model="internalFilters[filter.key]"
          :placeholder="filter.label"
          :clearable="true"
          @input="handleFilter"
        />
        <el-select
          v-else-if="filter.type === 'select'"
          v-model="internalFilters[filter.key]"
          :placeholder="filter.label"
          :clearable="true"
          @change="handleFilter"
        >
          <el-option
            v-for="option in filter.options"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <el-date-picker
          v-else-if="filter.type === 'date'"
          v-model="internalFilters[filter.key]"
          type="date"
          :placeholder="filter.label"
          :clearable="true"
          @change="handleFilter"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'filter', 'reset'])

const internalFilters = reactive({})

props.filters.forEach(filter => {
  internalFilters[filter.key] = ''
})

watch(
  () => props.modelValue,
  (newVal) => {
    Object.keys(newVal).forEach(key => {
      internalFilters[key] = newVal[key]
    })
  },
  { immediate: true, deep: true }
)

const handleFilter = () => {
  emit('update:modelValue', { ...internalFilters })
  emit('filter', { ...internalFilters })
}

const handleReset = () => {
  props.filters.forEach(filter => {
    internalFilters[filter.key] = ''
  })
  emit('update:modelValue', { ...internalFilters })
  emit('reset')
}

defineExpose({
  reset: handleReset
})
</script>

<style scoped>
.common-filter {
  margin-bottom: 20px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
  border: 1px solid #eee;
}
</style>
