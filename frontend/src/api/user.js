import axios from 'axios'

const api = axios.create({
  baseURL: '/api/user'
})

api.interceptors.response.use(res => {
  if (res.data.code === 200) {
    return res.data
  }
  return Promise.reject(res.data)
})

export function getUsers() {
  return api.get('/api/users')
}

export function getUser(id) {
  return api.get(`/api/users/${id}`)
}

export function createUser(data) {
  return api.post('/api/users', data)
}

export function updateUser(id, data) {
  return api.put(`/api/users/${id}`, data)
}

export function deleteUser(id) {
  return api.delete(`/api/users/${id}`)
}
