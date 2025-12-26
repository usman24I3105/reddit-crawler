import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api } from '../api/client'
import PostCard from '../components/PostCard'
import Loader from '../components/Loader'

const Dashboard = () => {
  const { workerId, logout } = useAuth()
  const navigate = useNavigate()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all') // all, pending, in_progress

  const fetchPosts = async () => {
    try {
      setError('')
      const status = filter === 'all' ? null : filter
      const data = await api.getPosts(status)
      setPosts(data)
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to load posts. Please try again.'
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchPosts()
  }, [filter])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchPosts()
  }

  const pendingCount = posts.filter(p => p.status === 'pending').length
  const inProgressCount = posts.filter(p => p.status === 'in_progress').length

  return (
    <div className="min-h-screen bg-reddit-light">
      {/* Reddit-style Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-4">
              <div 
                className="flex items-center gap-2 cursor-pointer"
                onClick={() => navigate('/dashboard')}
              >
                <div className="w-8 h-8 bg-reddit-orange rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-sm">R</span>
                </div>
                <span className="text-xl font-bold text-gray-900 hidden sm:inline">
                  Worker Dashboard
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600">
                <span className="font-medium">u/{workerId}</span>
              </div>
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
                title="Refresh"
              >
                <svg 
                  className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              <button
                onClick={logout}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-full transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats & Filters */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  filter === 'all'
                    ? 'bg-reddit-orange text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                All ({posts.length})
              </button>
              <button
                onClick={() => setFilter('pending')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  filter === 'pending'
                    ? 'bg-reddit-orange text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                Pending ({pendingCount})
              </button>
              <button
                onClick={() => setFilter('in_progress')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  filter === 'in_progress'
                    ? 'bg-reddit-orange text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                In Progress ({inProgressCount})
              </button>
            </div>
          </div>
          
          {refreshing && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <div className="w-4 h-4 border-2 border-reddit-orange border-t-transparent rounded-full animate-spin"></div>
              <span>Refreshing...</span>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded animate-slide-up">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <Loader size="lg" />
          </div>
        ) : posts.length === 0 ? (
          <div className="bg-white rounded-md border border-gray-200 p-12 text-center animate-fade-in">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <p className="text-gray-500 text-lg font-medium mb-2">No posts available</p>
            <p className="text-gray-400 text-sm">
              {filter === 'all' 
                ? 'Check back later or refresh to see new posts'
                : `No ${filter.replace('_', ' ')} posts at the moment`
              }
            </p>
            <button
              onClick={handleRefresh}
              className="mt-4 px-4 py-2 bg-reddit-orange text-white rounded-full text-sm font-medium hover:bg-orange-600 transition-colors"
            >
              Refresh
            </button>
          </div>
        ) : (
          <div className="space-y-2 animate-fade-in">
            {posts.map((post, index) => (
              <div key={post.id || post.reddit_post_id} style={{ animationDelay: `${index * 0.05}s` }}>
                <PostCard post={post} />
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard
