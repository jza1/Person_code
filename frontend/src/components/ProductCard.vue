<template>
  <el-card class="product-card" shadow="hover">
    <img :src="product.image" class="product-image" />
    <h3>{{ product.name }}</h3>
    <p class="description">{{ product.description }}</p>
    <div class="price-row">
      <span class="price">¥{{ product.price.toFixed(2) }}</span>
      <span class="stock">库存: {{ product.stock }}</span>
    </div>
    <el-button type="primary" style="width: 100%" @click="$emit('add-to-cart', product)">
      加入购物车
    </el-button>
  </el-card>
</template>

<script setup>
defineProps(['product'])
defineEmits(['add-to-cart'])
</script>

<style scoped>
.product-card {
  margin-bottom: 20px;
}
.product-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
}
.product-card h3 {
  margin: 10px 0;
  font-size: 16px;
}
.description {
  color: #999;
  font-size: 12px;
  height: 36px;
  overflow: hidden;
}
.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
}
.price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}
.stock {
  color: #999;
  font-size: 12px;
}
</style>
