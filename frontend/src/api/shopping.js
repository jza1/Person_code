import axios from 'axios'

const api = axios.create({
  baseURL: '/api/shop'
})

api.interceptors.response.use(res => {
  if (res.data.code === 200) {
    return res.data
  }
  return Promise.reject(res.data)
})

export function getProducts() {
  return api.get('/api/products')
}

export function getProduct(id) {
  return api.get(`/api/products/${id}`)
}

export function createProduct(data) {
  return api.post('/api/products', data)
}

export function getCart(userId) {
  return api.get(`/api/cart/${userId}`)
}

export function addToCart(data) {
  return api.post('/api/cart', data)
}

export function updateCart(id, quantity) {
  return api.put(`/api/cart/${id}`, { quantity })
}

export function deleteCartItem(id) {
  return api.delete(`/api/cart/${id}`)
}

export function createOrder(data) {
  return api.post('/api/orders', data)
}

export function getOrders(userId) {
  return api.get(`/api/orders/${userId}`)
}

export function getOrderDetail(id) {
  return api.get(`/api/orders/detail/${id}`)
}
