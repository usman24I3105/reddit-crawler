/**
 * Mock API client
 * Simulates FastAPI backend responses
 */

import {
  getMockPosts,
  assignMockPost,
  replyToMockPost,
  mockLogin,
} from './mockData.js'

/**
 * Check if mock API should be used
 */
export const useMockAPI = () => {
  const useMock = import.meta.env.VITE_USE_MOCK_API === 'true'
  
  // Log in development
  if (import.meta.env.DEV && useMock) {
    console.log('%c🔧 Mock API Enabled', 'color: #10b981; font-weight: bold; font-size: 14px;')
    console.log('Using mock API - backend not required')
  }
  
  return useMock
}

/**
 * Mock API client
 * Matches the real API interface exactly
 */
export const mockApi = {
  /**
   * Login
   */
  login: async (email, password) => {
    return await mockLogin(email, password)
  },

  /**
   * Get posts
   */
  getPosts: async (status = 'pending', subreddit = null, limit = null) => {
    return await getMockPosts(status, subreddit, limit)
  },

  /**
   * Assign post
   */
  assignPost: async (postId, workerId) => {
    return await assignMockPost(postId, workerId)
  },

  /**
   * Reply to post
   */
  replyToPost: async (postId, commentText, workerId) => {
    return await replyToMockPost(postId, commentText, workerId)
  },
}

