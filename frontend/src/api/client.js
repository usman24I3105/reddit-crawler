import axios from 'axios'
import { useMockAPI, mockApi } from './mockClient.js'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * Real API implementation
 */
const realApi = {
  // Auth
  login: async (email, password) => {
    // Real login endpoint
    const response = await apiClient.post('/auth/login', { email, password })
    const data = response.data
    // Store token for consistency
    localStorage.setItem('auth_token', data.token)
    localStorage.setItem('worker_id', data.worker_id)
    return data
  },

  // Posts
  getPosts: async (status = 'pending', subreddit = null, limit = null) => {
    const params = { status }
    if (subreddit) params.subreddit = subreddit
    if (limit) params.limit = limit  // Only add limit if specified
    const response = await apiClient.get('/posts', { params })
    return response.data
  },

  assignPost: async (postId, workerId) => {
    const response = await apiClient.post(`/posts/${postId}/assign`, {
      worker_id: workerId,
    })
    return response.data
  },

  replyToPost: async (postId, commentText, workerId) => {
    const response = await apiClient.post(`/posts/${postId}/reply`, {
      comment_text: commentText,
      worker_id: workerId,
    })
    return response.data
  },

  // Comments
  getComments: async (postId, limit = 50, fetchFromReddit = false) => {
    const params = { limit, fetch_from_reddit: fetchFromReddit }
    const response = await apiClient.get(`/posts/${postId}/comments`, { params })
    return response.data
  },
}

/**
 * API interface that switches between mock and real
 */
export const api = {
  login: async (email, password) => {
    if (useMockAPI()) {
      const result = await mockApi.login(email, password)
      // Store token for consistency
      localStorage.setItem('auth_token', result.token)
      localStorage.setItem('worker_id', result.worker_id)
      return result
    } else {
      return await realApi.login(email, password)
    }
  },

  getPosts: async (status = 'pending', subreddit = null, limit = null) => {
    if (useMockAPI()) {
      return await mockApi.getPosts(status, subreddit, limit)
    } else {
      return await realApi.getPosts(status, subreddit, limit)
    }
  },

  assignPost: async (postId, workerId) => {
    if (useMockAPI()) {
      return await mockApi.assignPost(postId, workerId)
    } else {
      return await realApi.assignPost(postId, workerId)
    }
  },

  replyToPost: async (postId, commentText, workerId) => {
    if (useMockAPI()) {
      return await mockApi.replyToPost(postId, commentText, workerId)
    } else {
      return await realApi.replyToPost(postId, commentText, workerId)
    }
  },

  getComments: async (postId, limit = 50, fetchFromReddit = false) => {
    if (useMockAPI()) {
      return await mockApi.getComments ? await mockApi.getComments(postId, limit, fetchFromReddit) : []
    } else {
      return await realApi.getComments(postId, limit, fetchFromReddit)
    }
  },
}

export default apiClient

