import React, { useState } from 'react'
import Loader from './Loader'

const ReplyForm = ({ postId, workerId, onSuccess, onCancel }) => {
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const maxLength = 10000

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!comment.trim()) {
      setError('Please enter a reply')
      return
    }

    if (comment.length > maxLength) {
      setError(`Reply must be less than ${maxLength} characters`)
      return
    }

    setLoading(true)

    try {
      const { api } = await import('../api/client')
      await api.replyToPost(postId, comment, workerId)
      onSuccess()
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to submit reply. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  const remainingChars = maxLength - comment.length
  const isNearLimit = remainingChars < 100

  return (
    <div className="reddit-card p-6 animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-reddit-orange rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </div>
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Write Your Reply</h3>
          <p className="text-sm text-gray-500">Your reply will be posted to Reddit</p>
        </div>
      </div>
      
      {error && (
        <div className="mb-4 bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded animate-slide-up">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="comment" className="block text-sm font-medium text-gray-700 mb-2">
            Your Reply
          </label>
          <textarea
            id="comment"
            rows={10}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-reddit-orange focus:border-transparent transition-all resize-y font-sans text-gray-900"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            disabled={loading}
            placeholder="Write your reply here... You can use Markdown formatting."
            maxLength={maxLength}
          />
          <div className={`mt-2 flex justify-between text-xs ${
            isNearLimit ? 'text-red-600 font-medium' : 'text-gray-500'
          }`}>
            <span>{comment.length.toLocaleString()} / {maxLength.toLocaleString()} characters</span>
            {remainingChars < 500 && (
              <span>{remainingChars} characters remaining</span>
            )}
          </div>
        </div>

        {/* Formatting Help */}
        <div className="mb-6 p-3 bg-gray-50 rounded-lg text-xs text-gray-600">
          <p className="font-medium mb-1">Formatting tips:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Use **bold** for <strong>bold text</strong></li>
            <li>Use *italic* for <em>italic text</em></li>
            <li>Use &gt; for quotes</li>
          </ul>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading || !comment.trim()}
            className="flex-1 reddit-button-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Submitting...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                Submit Reply
              </>
            )}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              className="px-6 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

export default ReplyForm
