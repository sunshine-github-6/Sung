<template>
  <div class="common-table">
    <el-table
      :data="displayData"
      v-loading="loading"
      stripe
      style="width: 100%"
      :height="height"
      :max-height="maxHeight"
      :row-key="rowKey"
      :header-cell-style="headerCellStyle"
      :cell-style="cellStyle"
      @selection-change="handleSelectionChange"
    >
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
        fixed="left"
      />

      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :min-width="column.minWidth"
        :fixed="column.fixed"
        :sortable="column.sortable"
        :formatter="column.formatter"
        :show-overflow-tooltip="column.showOverflowTooltip !== false"
      >
        <template v-if="column.slot" #default="{ row }">
          <slot :name="column.slot" :row="row" :column="column" />
        </template>
      </el-table-column>

      <el-table-column
        v-if="showActions"
        label="操作"
        :width="actionWidth"
        :fixed="actionFixed || 'right'"
      >
        <template #default="{ row }">
          <slot name="actions" :row="row">
            <el-button
              v-if="showEdit"
              size="small"
              :type="editType"
              :icon="Edit"
              @click="$emit('edit', row)"
            >
              {{ editText }}
            </el-button>
            <el-button
              v-if="showDelete"
              size="small"
              :type="deleteType"
              :icon="Delete"
              @click="$emit('delete', row)"
            >
              {{ deleteText }}
            </el-button>
          </slot>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Edit, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  height: {
    type: [String, Number],
    default: 'calc(100vh - 280px)'
  },
  maxHeight: {
    type: [String, Number],
    default: undefined
  },
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  showSelection: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showEdit: {
    type: Boolean,
    default: true
  },
  showDelete: {
    type: Boolean,
    default: true
  },
  editText: {
    type: String,
    default: '编辑'
  },
  deleteText: {
    type: String,
    default: '删除'
  },
  editType: {
    type: String,
    default: 'primary'
  },
  deleteType: {
    type: String,
    default: 'danger'
  },
  actionWidth: {
    type: Number,
    default: 150
  },
  actionFixed: {
    type: String,
    default: 'right'
  },
  headerCellStyle: {
    type: Object,
    default: () => ({ background: '#f5f7fa', color: '#606266' })
  },
  cellStyle: {
    type: Object,
    default: () => ({ padding: '10px 0' })
  }
})

const emit = defineEmits([
  'edit',
  'delete',
  'selection-change',
  'row-click'
])

const displayData = computed(() => {
  if (!props.showPagination) {
    return props.data
  }
  const start = (props.currentPage - 1) * props.pageSize
  const end = start + props.pageSize
  return props.data.slice(start, end)
})

const handleSelectionChange = (selection) => {
  emit('selection-change', selection)
}
</script>

<style scoped>
.common-table {
  width: 100%;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table__row:hover > td) {
  background-color: #f5f7fa;
}

:deep(.el-table td) {
  border-bottom: 1px solid #eee;
}

:deep(.el-table th.is-leaf) {
  border-bottom: 1px solid #dfe4ed;
}
</style>
