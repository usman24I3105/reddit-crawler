import React from 'react'
import { useNavigate } from 'react-router-dom'

const PostCard = ({ post }) => {
  const navigate = useNavigate()

  const truncate = (text, maxLength) => {
    if (!text) return ''
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  }

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

  return (
    <div className="reddit-card p-4 mb-2 animate-fade-in">
      <div className="flex">
        {/* Upvote Section - Reddit Style */}
        <div className="flex flex-col items-center mr-3 pt-1">
          <button className="text-gray-400 hover:text-reddit-orange transition-colors p-1">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
          </button>
          <span className="text-xs font-semibold text-gray-700 py-1">
            {formatNumber(post.upvotes || 0)}
          </span>
          <button className="text-gray-400 hover:text-blue-600 transition-colors p-1">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {/* Main Content */}
        <div className="flex-1 min-w-0">
          {/* Subreddit & Metadata */}
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <a 
              href={`https://reddit.com/r/${post.subreddit}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-bold text-gray-600 hover:underline"
              onClick={(e) => e.stopPropagation()}
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
          <h3 
            className="text-lg font-medium text-gray-900 mb-2 cursor-pointer hover:text-reddit-orange transition-colors line-clamp-2"
            onClick={() => navigate(`/posts/${post.reddit_post_id}`)}
          >
            {post.title}
          </h3>
          
          {/* Reddit Link Button */}
          {post.reddit_url && (
            <a
              href={post.reddit_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="inline-flex items-center gap-1 text-xs text-reddit-orange hover:text-orange-600 font-medium mb-2 transition-colors"
            >
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
              </svg>
              Open on Reddit
            </a>
          )}

          {/* Body Preview */}
          {post.body && (
            <p className="text-sm text-gray-700 mb-3 line-clamp-3">
              {truncate(post.body, 200)}
            </p>
          )}

          {/* Engagement Stats & Actions */}
          <div className="flex items-center gap-4 text-xs text-gray-500">
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
            <button
              onClick={() => navigate(`/posts/${post.reddit_post_id}`)}
              className="ml-auto px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-full text-xs transition-colors"
            >
              View & Reply →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PostCard
