<template>
  <div class="favorites">
    <div class="page-header">
      <div class="header-left">
        <el-checkbox v-model="selectAll" @change="toggleSelectAll" v-if="favorites.length > 0">
          全选
        </el-checkbox>
        <h2>我的收藏</h2>
        <span class="count">({{ favorites.length }}件)</span>
      </div>
      <div class="header-actions">
        <el-button v-if="selectedIds.length > 0" type="danger" @click="handleBatchRemove">
          批量取消收藏 ({{ selectedIds.length }})
        </el-button>
        <el-button type="primary" @click="handleCheckout" :disabled="selectedIds.length === 0">
          结算选中 ({{ selectedIds.length }})
        </el-button>
      </div>
    </div>

    <el-empty v-if="favorites.length === 0 && !loading" description="暂无收藏商品">
      <el-button type="primary" @click="$router.push('/')">去商城逛逛</el-button>
    </el-empty>

    <div v-else class="favorites-list">
      <div v-for="item in favorites" :key="item.id" class="favorite-item" :class="{ selected: selectedMap[item.id] }">
        <el-checkbox v-model="selectedMap[item.id]" />
        <img :src="item.product?.image || defaultImage" class="product-image" @error="handleImageError" />
        <div class="product-info">
          <h3 class="product-name">{{ item.product?.name }}</h3>
          <p class="product-desc">{{ item.product?.description }}</p>
          <div class="price-row">
            <span class="price">¥{{ item.product?.price.toFixed(2) }}</span>
            <span class="stock">库存: {{ item.product?.stock }}</span>
          </div>
        </div>
        <div class="item-actions">
          <el-button type="primary" size="small" @click="handleBuyNow(item.product)" :disabled="!item.product || item.product.stock === 0">
            立即购买
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFavorites, removeFavoriteItem } from '@/api/shopping'

const router = useRouter()
const favorites = ref([])
const loading = ref(false)
const selectedMap = ref({})
const currentUser = ref(null)

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZGIi8+CjxwYXRoIGQ9Ik02MCAxMjBMODUgODVMMTE1IDExMEwxNDUgNzVMMTcwIDEyMEg2MFoiIGZpbGw9IiNEOUQzREMvPgo8Y2lyY2xlIGN4PSI4NSIgY3k9IjgwIiByPSIxNSIgZmlsbD0iI0Q5RDNEQyIvPgo8L3N2Zz4K'

const selectedIds = computed(() => {
  return Object.keys(selectedMap.value).filter(id => selectedMap.value[id])
})

const selectAll = computed({
  get: () => {
    return favorites.value.length > 0 && selectedIds.value.length === favorites.value.length
  },
  set: (value) => {
    favorites.value.forEach(item => {
      selectedMap.value[item.id] = value
    })
  }
})

onMounted(() => {
  loadUser()
  loadFavorites()
})

function loadUser() {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
}

async function loadFavorites() {
  if (!currentUser.value) return
  loading.value = true
  try {
    const res = await getFavorites(currentUser.value.id)
    favorites.value = res.data || []
    favorites.value.forEach(item => {
      if (selectedMap.value[item.id] === undefined) {
        selectedMap.value[item.id] = false
      }
    })
  } catch (e) {
    ElMessage.error('加载收藏失败')
  } finally {
    loading.value = false
  }
}

function toggleSelectAll() {
}

async function handleRemove(id) {
  await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await removeFavoriteItem(Number(id))
    favorites.value = favorites.value.filter(f => f.id !== id)
    delete selectedMap.value[id]
    ElMessage.success('已取消收藏')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handleBatchRemove() {
  await ElMessageBox.confirm(`确定要取消收藏选中的 ${selectedIds.value.length} 件商品吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    for (const id of selectedIds.value) {
      await removeFavoriteItem(Number(id))
    }
    favorites.value = favorites.value.filter(f => !selectedIds.value.includes(String(f.id)))
    selectedIds.value.forEach(id => delete selectedMap.value[id])
    ElMessage.success('已取消收藏')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function handleBuyNow(product) {
  if (!product) return
  if (product.stock < 1) {
    ElMessage.warning('该商品库存不足')
    return
  }
  const checkoutItem = {
    id: Date.now(),
    product_id: product.id,
    quantity: 1,
    product: product
  }
  localStorage.setItem('checkoutItems', JSON.stringify([checkoutItem]))
  router.push('/orders?checkout=true')
}

function handleCheckout() {
  const selectedItems = favorites.value.filter(f => selectedIds.value.includes(String(f.id)))
  const validItems = selectedItems.filter(item => item.product && item.product.stock > 0)

  if (validItems.length === 0) {
    ElMessage.warning('选中的商品库存不足')
    return
  }

  const checkoutItems = validItems.map((item, index) => ({
    id: Date.now() + index,
    product_id: item.product.id,
    quantity: 1,
    product: item.product
  }))

  localStorage.setItem('checkoutItems', JSON.stringify(checkoutItems))
  router.push('/orders?checkout=true')
}

function handleImageError(e) {
  e.target.src = defaultImage
}
</script>

<style scoped>
.favorites {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
}

.count {
  color: #999;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.favorite-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.favorite-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.favorite-item.selected {
  box-shadow: 0 0 0 2px #409eff;
}

.product-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  background: #f5f7fa;
}

.product-info {
  flex: 1;
}

.product-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.product-desc {
  margin: 0 0 8px 0;
  color: #999;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price-row {
  display: flex;
  gap: 16px;
  align-items: center;
}

.price {
  color: #ff4d4f;
  font-size: 20px;
  font-weight: bold;
}

.stock {
  color: #999;
  font-size: 14px;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
