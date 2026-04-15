<template>
  <div class="mall">
    <h2>商城首页</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="product in products" :key="product.id">
        <product-card :product="product" @add-to-cart="handleAddToCart" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProducts, addToCart } from '@/api/shopping'
import { ElMessage } from 'element-plus'
import ProductCard from '@/components/ProductCard.vue'

const products = ref([])
const currentUser = ref(null)

onMounted(() => {
  loadProducts()
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
})

async function loadProducts() {
  const res = await getProducts()
  products.value = res.data
}

async function handleAddToCart(product) {
  if (!currentUser.value) {
    ElMessage.warning('请先选择用户')
    return
  }
  await addToCart({
    user_id: currentUser.value.id,
    product_id: product.id,
    quantity: 1
  })
  ElMessage.success('已加入购物车')
}
</script>

<style scoped>
.mall h2 {
  margin-bottom: 20px;
}
</style>
