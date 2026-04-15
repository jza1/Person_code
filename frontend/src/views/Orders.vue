<template>
  <div class="orders">
    <h2>我的订单</h2>

    <el-card v-if="showCheckout" class="checkout-card">
      <template #header>
        <div class="card-header">
          <span>确认订单</span>
          <el-button link @click="showCheckout = false">取消</el-button>
        </div>
      </template>
      <el-table :data="checkoutItems">
        <el-table-column prop="product.name" label="商品" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column label="单价">
          <template #default="{ row }">¥{{ row.product.price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="小计">
          <template #default="{ row }">¥{{ (row.product.price * row.quantity).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
      <div class="checkout-footer">
        <span class="total">总计: ¥{{ checkoutTotal.toFixed(2) }}</span>
        <el-button type="primary" size="large" :loading="creating" @click="submitOrder">提交订单</el-button>
      </div>
    </el-card>

    <el-timeline v-if="orders.length > 0">
      <el-timeline-item
        v-for="order in orders"
        :key="order.id"
        :timestamp="formatDate(order.created_at)"
        placement="top"
      >
        <el-card>
          <div class="order-header">
            <span class="order-id">订单 #{{ order.id }}</span>
            <el-tag :type="order.status === 'paid' ? 'success' : 'info'">
              {{ order.status === 'paid' ? '已支付' : order.status }}
            </el-tag>
          </div>
          <el-table :data="order.items" size="small">
            <el-table-column prop="product_id" label="商品ID" width="100" />
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="price" label="单价">
              <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
            </el-table-column>
          </el-table>
          <div class="order-total">订单总额: <span class="price">¥{{ order.total_price.toFixed(2) }}</span></div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
    <el-empty v-else description="暂无订单" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getOrders, createOrder } from '@/api/shopping'
import { ElMessage } from 'element-plus'

const route = useRoute()
const orders = ref([])
const showCheckout = ref(false)
const checkoutItems = ref([])
const creating = ref(false)
const currentUser = ref(null)

const checkoutTotal = computed(() => {
  return checkoutItems.value.reduce((sum, item) => sum + item.product.price * item.quantity, 0)
})

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
    loadOrders()
  }
  if (route.query.checkout) {
    const items = localStorage.getItem('checkoutItems')
    if (items) {
      checkoutItems.value = JSON.parse(items)
      showCheckout.value = true
      localStorage.removeItem('checkoutItems')
    }
  }
})

async function loadOrders() {
  if (!currentUser.value) return
  const res = await getOrders(currentUser.value.id)
  orders.value = res.data || []
}

async function submitOrder() {
  creating.value = true
  try {
    await createOrder({
      user_id: currentUser.value.id,
      items: checkoutItems.value.map(item => ({
        user_id: currentUser.value.id,
        product_id: item.product_id,
        quantity: item.quantity
      }))
    })
    ElMessage.success('订单创建成功')
    showCheckout.value = false
    checkoutItems.value = []
    loadOrders()
  } finally {
    creating.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.orders h2 {
  margin-bottom: 20px;
}
.checkout-card {
  margin-bottom: 30px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.checkout-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
}
.checkout-footer .total {
  font-size: 20px;
  font-weight: bold;
  color: #f56c6c;
}
.order-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}
.order-id {
  font-weight: bold;
}
.order-total {
  margin-top: 15px;
  text-align: right;
}
.order-total .price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}
</style>
