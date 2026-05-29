<template>
  <div class="common-pagination">
    <el-pagination
      v-model:current-page="internalCurrentPage"
      v-model:page-size="internalPageSize"
      :total="total"
      :page-sizes="pageSizes"
      :background="background"
      :small="small"
      :layout="layout"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  total: {
    type: Number,
    default: 0
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  background: {
    type: Boolean,
    default: true
  },
  small: {
    type: Boolean,
    default: false
  },
  layout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  }
})

const emit = defineEmits(['update:currentPage', 'update:pageSize', 'change'])

const internalCurrentPage = computed({
  get: () => props.currentPage,
  set: (val) => emit('update:currentPage', val)
})

const internalPageSize = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})

const handleSizeChange = (size) => {
  emit('update:pageSize', size)
  emit('change', { type: 'size', page: internalCurrentPage.value, size })
}

const handleCurrentChange = (page) => {
  emit('update:currentPage', page)
  emit('change', { type: 'page', page, size: internalPageSize.value })
}
</script>

<style scoped>
.common-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}
</style>
