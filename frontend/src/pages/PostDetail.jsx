import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api } from '../api/client'
import Loader from '../components/Loader'
import ReplyForm from '../components/ReplyForm'

const PostDetail = () => {
  const { postId } = useParams()
  const navigate = useNavigate()
  const { workerId } = useAuth()
  const [post, setPost] = useState(null)
  const [loading, setLoading] = useState(true)
  const [assigning, setAssigning] = useState(false)
  const [showReplyForm, setShowReplyForm] = useState(false)
  const [error, setError] = useState('')
  const [comments, setComments] = useState([])
  const [loadingComments, setLoadingComments] = useState(false)
  const [showComments, setShowComments] = useState(false)

  useEffect(() => {
    const fetchPost = async () => {
      try {
        setError('')
        let posts = await api.getPosts('pending', null, 1000)
        let foundPost = posts.find((p) => p.reddit_post_id === postId)
        
        if (!foundPost) {
          try {
            posts = await api.getPosts(null, null, 1000)
            foundPost = posts.find((p) => p.reddit_post_id === postId)
          } catch (e) {
            try {
              const inProgress = await api.getPosts('in_progress', null, 1000)
              foundPost = inProgress.find((p) => p.reddit_post_id === postId)
            } catch (e2) {}
            
            if (!foundPost) {
              try {
                const replied = await api.getPosts('replied', null, 1000)
                foundPost = replied.find((p) => p.reddit_post_id === postId)
              } catch (e3) {}
            }
          }
        }
        
        if (foundPost) {
          setPost(foundPost)
        } else {
          setError('Post not found')
        }
      } catch (err) {
        setError(
          err.response?.data?.detail || 'Failed to load post. Please try again.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchPost()
  }, [postId])

  const fetchComments = async (fetchFromReddit = false) => {
    setLoadingComments(true)
    try {
      const data = await api.getComments(postId, 50, fetchFromReddit)
      setComments(data)
      setShowComments(true)
    } catch (err) {
      console.error('Failed to fetch comments:', err)
    } finally {
      setLoadingComments(false)
    }
  }

  const handleAssign = async () => {
    setAssigning(true)
    setError('')

    try {
      await api.assignPost(postId, workerId)
      const posts = await api.getPosts(null, null, 1000)
      const updated = posts.find((p) => p.reddit_post_id === postId)
      if (updated) setPost(updated)
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to assign post. Please try again.'
      )
    } finally {
      setAssigning(false)
    }
  }

  const handleReplySuccess = () => {
    navigate('/dashboard')
  }

  const canReply = post?.status === 'in_progress' && post?.assigned_to === workerId
  const isAssigned = post?.assigned_to === workerId

  const formatNumber = (num) => {
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
    return num.toString()
  }

  const getTimeAgo = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'just now'
    if (diffInHours < 24) return `${diffInHours}h ago`
    const diffInDays = Math.floor(diffInHours / 24)
    if (diffInDays < 7) return `${diffInDays}d ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-reddit-light flex items-center justify-center">
        <Loader size="lg" />
      </div>
    )
  }

  if (error && !post) {
    return (
      <div className="min-h-screen bg-reddit-light flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full animate-fade-in">
          <div className="text-center">
            <svg className="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-600 mb-4 font-medium">{error}</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="reddit-button-primary"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!post) {
    return (
      <div className="min-h-screen bg-reddit-light flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full animate-fade-in">
          <p className="text-gray-600 mb-4 text-center">Post not found</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full reddit-button-primary"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-reddit-light">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-14">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-medium">Back to Dashboard</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {error && (
          <div className="mb-4 bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded animate-slide-up">
            {error}
          </div>
        )}

        {!showReplyForm ? (
          <div className="reddit-card p-6 animate-fade-in">
            {/* Upvote Section */}
            <div className="flex gap-4">
              <div className="flex flex-col items-center pt-1">
                <button className="text-gray-400 hover:text-reddit-orange transition-colors p-1">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                  </svg>
                </button>
                <span className="text-sm font-bold text-gray-700 py-2">
                  {formatNumber(post.upvotes || 0)}
                </span>
                <button className="text-gray-400 hover:text-blue-600 transition-colors p-1">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>

              <div className="flex-1">
                {/* Subreddit & Metadata */}
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <a 
                    href={`https://reddit.com/r/${post.subreddit}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-bold text-gray-600 hover:underline"
                  >
                    r/{post.subreddit}
                  </a>
                  <span className="text-xs text-gray-500">•</span>
                  <span className="text-xs text-gray-500">
                    Posted by u/{post.author}
                  </span>
                  <span className="text-xs text-gray-500">•</span>
                  <span className="text-xs text-gray-500">
                    {getTimeAgo(post.fetched_at)}
                  </span>
                </div>

                {/* Title */}
                <h1 className="text-2xl font-semibold text-gray-900 mb-4 leading-tight">
                  {post.title}
                </h1>

                {/* Body */}
                {post.body && (
                  <div className="mb-6">
                    <div className="prose max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {post.body}
                    </div>
                  </div>
                )}

                {/* Engagement Stats */}
                <div className="flex items-center gap-4 mb-6 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <span>{formatNumber(post.comments || 0)} comments</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    <span>Score: {formatNumber(post.score || 0)}</span>
                  </div>
                </div>

                {/* Status Badges */}
                <div className="flex items-center gap-2 mb-6 flex-wrap">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                    post.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    post.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {post.status === 'pending' ? '⏳ Pending' :
                     post.status === 'in_progress' ? '🔄 In Progress' :
                     '✅ Replied'}
                  </span>
                  {post.assigned_to && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                      👤 {post.assigned_to}
                    </span>
                  )}
                </div>

                {/* Reddit Link */}
                {(post.reddit_url || post.permalink) && (
                  <div className="mb-6">
                    <a
                      href={post.reddit_url || `https://reddit.com${post.permalink}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-reddit-orange hover:text-orange-600 font-medium text-sm transition-colors"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                        <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                      </svg>
                      View on Reddit
                    </a>
                  </div>
                )}

                {/* Comments Section */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg font-semibold text-gray-900">
                      Comments ({post.comments || 0})
                    </h2>
                    <div className="flex gap-2">
                      {!showComments ? (
                        <button
                          onClick={() => fetchComments(false)}
                          disabled={loadingComments}
                          className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-full transition-colors disabled:opacity-50"
                        >
                          {loadingComments ? 'Loading...' : 'Load Comments'}
                        </button>
                      ) : (
                        <button
                          onClick={() => fetchComments(true)}
                          disabled={loadingComments}
                          className="px-3 py-1.5 bg-reddit-orange hover:bg-orange-600 text-white text-sm font-medium rounded-full transition-colors disabled:opacity-50"
                        >
                          {loadingComments ? 'Refreshing...' : 'Refresh from Reddit'}
                        </button>
                      )}
                    </div>
                  </div>

                  {showComments && (
                    <div className="space-y-3">
                      {loadingComments ? (
                        <div className="flex justify-center py-8">
                          <Loader size="md" />
                        </div>
                      ) : comments.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                          <p>No comments found</p>
                        </div>
                      ) : (
                        comments.map((comment) => (
                          <div
                            key={comment.id || comment.reddit_comment_id}
                            className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-semibold text-gray-700">
                                  u/{comment.author}
                                </span>
                                {comment.upvotes > 0 && (
                                  <span className="text-xs text-gray-500">
                                    • {formatNumber(comment.upvotes)} upvotes
                                  </span>
                                )}
                              </div>
                              {comment.reddit_url && (
                                <a
                                  href={comment.reddit_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs text-reddit-orange hover:text-orange-600"
                                >
                                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                                  </svg>
                                </a>
                              )}
                            </div>
                            <p className="text-sm text-gray-700 whitespace-pre-wrap">
                              {comment.body}
                            </p>
                            {comment.created_utc && (
                              <p className="text-xs text-gray-500 mt-2">
                                {getTimeAgo(comment.created_utc)}
                              </p>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4 border-t border-gray-200">
                  {!isAssigned && post.status === 'pending' && (
                    <button
                      onClick={handleAssign}
                      disabled={assigning}
                      className="reddit-button-primary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {assigning ? (
                        <span className="flex items-center gap-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          Assigning...
                        </span>
                      ) : (
                        '📌 Assign to Me'
                      )}
                    </button>
                  )}
                  {canReply && (
                    <button
                      onClick={() => setShowReplyForm(true)}
                      className="reddit-button-primary bg-green-600 hover:bg-green-700 focus:ring-green-500"
                    >
                      💬 Write Reply
                    </button>
                  )}
                  {!canReply && isAssigned && (
                    <p className="text-sm text-gray-500 flex items-center">
                      Please assign this post to yourself first
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <ReplyForm
            postId={postId}
            workerId={workerId}
            onSuccess={handleReplySuccess}
            onCancel={() => setShowReplyForm(false)}
          />
        )}
      </main>
    </div>
  )
}

export default PostDetail
