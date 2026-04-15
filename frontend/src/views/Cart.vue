<template>
  <div class="cart">
    <h2>购物车</h2>
    <el-empty v-if="cartItems.length === 0" description="购物车是空的" />
    <el-table v-else :data="cartItems" style="width: 100%">
      <el-table-column label="商品" width="400">
        <template #default="{ row }">
          <div class="product-info">
            <img :src="row.product?.image" class="thumb" />
            <div class="info">
              <div class="name">{{ row.product?.name }}</div>
              <div class="price">¥{{ row.product?.price.toFixed(2) }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="数量" width="200">
        <template #default="{ row }">
          <el-input-number v-model="row.quantity" :min="1" @change="updateQuantity(row)" />
        </template>
      </el-table-column>
      <el-table-column label="小计">
        <template #default="{ row }">
          <span class="subtotal">¥{{ (row.product?.price * row.quantity).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button type="danger" size="small" link @click="removeItem(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div v-if="cartItems.length > 0" class="footer">
      <span class="total">总计: ¥{{ totalPrice.toFixed(2) }}</span>
      <el-button type="primary" size="large" @click="checkout">结算</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCart, updateCart, deleteCartItem } from '@/api/shopping'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const cartItems = ref([])
const currentUser = ref(null)

const totalPrice = computed(() => {
  return cartItems.value.reduce((sum, item) => {
    return sum + (item.product?.price || 0) * item.quantity
  }, 0)
})

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
    loadCart()
  } else {
    ElMessage.warning('请先选择用户')
  }
})

async function loadCart() {
  if (!currentUser.value) return
  const res = await getCart(currentUser.value.id)
  cartItems.value = res.data || []
}

async function updateQuantity(item) {
  await updateCart(item.id, item.quantity)
  ElMessage.success('已更新')
}

async function removeItem(item) {
  await ElMessageBox.confirm('确定删除此商品？')
  await deleteCartItem(item.id)
  cartItems.value = cartItems.value.filter(i => i.id !== item.id)
  ElMessage.success('已删除')
}

function checkout() {
  localStorage.setItem('checkoutItems', JSON.stringify(cartItems.value))
  router.push('/orders?checkout=true')
}
</script>

<style scoped>
.cart h2 {
  margin-bottom: 20px;
}
.product-info {
  display: flex;
  gap: 10px;
}
.product-info .thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
}
.product-info .name {
  font-weight: bold;
}
.product-info .price {
  color: #f56c6c;
}
.subtotal {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}
.footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
}
.total {
  font-size: 20px;
  font-weight: bold;
  color: #f56c6c;
}
</style>
