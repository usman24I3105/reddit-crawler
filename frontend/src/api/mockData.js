/**
 * Mock data storage for API mocking
 * Simulates in-memory database
 */

// Initial mock posts
let mockPosts = [
  {
    id: 1,
    reddit_post_id: 'abc123',
    subreddit: 'webdev',
    title: 'How do I deploy a FastAPI app?',
    body: "I'm looking for advice on deployment. What's the best way to deploy a FastAPI application? Should I use Docker, or is there a simpler approach?",
    author: 'dev_user',
    permalink: '/r/webdev/comments/abc123/how_do_i_deploy/',
    url: 'https://reddit.com/r/webdev/comments/abc123/',
    upvotes: 123,
    comments: 45,
    score: 123,
    status: 'pending',
    assigned_to: null,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    created_utc: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    fetched_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    reddit_post_id: 'def456',
    subreddit: 'python',
    title: 'Best practices for async Python?',
    body: 'I\'m working on a project that needs to handle many concurrent requests. What are the best practices for async Python development?',
    author: 'python_dev',
    permalink: '/r/python/comments/def456/best_practices/',
    url: 'https://reddit.com/r/python/comments/def456/',
    upvotes: 89,
    comments: 23,
    score: 89,
    status: 'pending',
    assigned_to: null,
    created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    created_utc: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    fetched_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 3,
    reddit_post_id: 'ghi789',
    subreddit: 'reactjs',
    title: 'React hooks performance tips?',
    body: 'Are there any performance tips for using React hooks? I\'m seeing some slowdowns in my app.',
    author: 'react_fan',
    permalink: '/r/reactjs/comments/ghi789/react_hooks/',
    url: 'https://reddit.com/r/reactjs/comments/ghi789/',
    upvotes: 156,
    comments: 67,
    score: 156,
    status: 'pending',
    assigned_to: null,
    created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    created_utc: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    fetched_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 4,
    reddit_post_id: 'jkl012',
    subreddit: 'webdev',
    title: 'Tailwind CSS vs styled-components?',
    body: 'Which do you prefer for styling React apps? I\'m trying to decide between Tailwind CSS and styled-components.',
    author: 'css_expert',
    permalink: '/r/webdev/comments/jkl012/tailwind_vs_styled/',
    url: 'https://reddit.com/r/webdev/comments/jkl012/',
    upvotes: 234,
    comments: 89,
    score: 234,
    status: 'pending',
    assigned_to: null,
    created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    created_utc: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    fetched_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 5,
    reddit_post_id: 'mno345',
    subreddit: 'python',
    title: 'SQLAlchemy ORM best practices?',
    body: 'What are the best practices for using SQLAlchemy ORM? I\'m new to it and want to make sure I\'m doing things right.',
    author: 'db_admin',
    permalink: '/r/python/comments/mno345/sqlalchemy_orm/',
    url: 'https://reddit.com/r/python/comments/mno345/',
    upvotes: 67,
    comments: 12,
    score: 67,
    status: 'pending',
    assigned_to: null,
    created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    created_utc: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    fetched_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
  },
]

// Mock users for authentication
const mockUsers = {
  'worker1@example.com': { password: 'password', workerId: 'worker1' },
  'worker2@example.com': { password: 'password', workerId: 'worker2' },
  'admin@example.com': { password: 'admin123', workerId: 'admin' },
}

/**
 * Simulate network delay
 */
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

/**
 * Simulate random network delay (300-800ms)
 */
const randomDelay = () => delay(300 + Math.random() * 500)

/**
 * Check if we should simulate an error
 */
const shouldFail = () => {
  const failRate = parseFloat(import.meta.env.VITE_MOCK_FAIL_RATE || '0')
  return Math.random() < failRate
}

/**
 * Get posts by status
 */
export const getMockPosts = async (status = null, subreddit = null, limit = 50) => {
  await randomDelay()

  if (shouldFail()) {
    throw {
      response: {
        status: 500,
        data: { detail: 'Internal server error (simulated)' },
      },
    }
  }

  let filtered = [...mockPosts]

  // Filter by status
  if (status) {
    filtered = filtered.filter((post) => post.status === status)
  }

  // Filter by subreddit
  if (subreddit) {
    filtered = filtered.filter((post) => post.subreddit === subreddit)
  }

  // Apply limit
  if (limit) {
    filtered = filtered.slice(0, limit)
  }

  return filtered
}

/**
 * Assign a post to a worker
 */
export const assignMockPost = async (postId, workerId) => {
  await randomDelay()

  if (shouldFail()) {
    throw {
      response: {
        status: 500,
        data: { detail: 'Failed to assign post (simulated error)' },
      },
    }
  }

  const post = mockPosts.find((p) => p.reddit_post_id === postId)

  if (!post) {
    throw {
      response: {
        status: 404,
        data: { detail: 'Post not found' },
      },
    }
  }

  if (post.status !== 'pending') {
    throw {
      response: {
        status: 400,
        data: { detail: 'Post is not pending' },
      },
    }
  }

  // Update post
  post.status = 'in_progress'
  post.assigned_to = workerId

  return {
    message: 'Post assigned successfully',
    post_id: postId,
    assigned_to: workerId,
  }
}

/**
 * Reply to a post
 */
export const replyToMockPost = async (postId, commentText, workerId) => {
  await randomDelay()

  if (shouldFail()) {
    throw {
      response: {
        status: 500,
        data: { detail: 'Failed to post reply (simulated error)' },
      },
    }
  }

  const post = mockPosts.find((p) => p.reddit_post_id === postId)

  if (!post) {
    throw {
      response: {
        status: 404,
        data: { detail: 'Post not found' },
      },
    }
  }

  if (post.assigned_to !== workerId) {
    throw {
      response: {
        status: 403,
        data: { detail: 'Post is not assigned to you' },
      },
    }
  }

  // Update post status and remove from pending list
  post.status = 'replied'
  post.assigned_to = workerId

  // Simulate comment ID
  const commentId = `comment_${Date.now()}`

  return {
    message: 'Comment posted successfully',
    post_id: postId,
    comment_id: commentId,
  }
}

/**
 * Mock login
 */
export const mockLogin = async (email, password) => {
  await randomDelay()

  if (shouldFail()) {
    throw {
      response: {
        status: 401,
        data: { detail: 'Invalid credentials (simulated error)' },
      },
    }
  }

  // Accept any email/password for mock, but prefer stored users
  const user = mockUsers[email] || { password: 'any', workerId: email.split('@')[0] }

  if (user.password !== password && password !== 'any') {
    throw {
      response: {
        status: 401,
        data: { detail: 'Invalid credentials' },
      },
    }
  }

  const token = `mock_jwt_token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

  return {
    token,
    worker_id: user.workerId,
  }
}

/**
 * Reset mock data (useful for testing)
 */
export const resetMockData = () => {
  // Reinitialize posts
  mockPosts = [
    {
      id: 1,
      reddit_post_id: 'abc123',
      subreddit: 'webdev',
      title: 'How do I deploy a FastAPI app?',
      body: "I'm looking for advice on deployment. What's the best way to deploy a FastAPI application?",
      author: 'dev_user',
      permalink: '/r/webdev/comments/abc123/how_do_i_deploy/',
      url: 'https://reddit.com/r/webdev/comments/abc123/',
      upvotes: 123,
      comments: 45,
      score: 123,
      status: 'pending',
      assigned_to: null,
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      created_utc: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      fetched_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 2,
      reddit_post_id: 'def456',
      subreddit: 'python',
      title: 'Best practices for async Python?',
      body: 'I\'m working on a project that needs to handle many concurrent requests.',
      author: 'python_dev',
      permalink: '/r/python/comments/def456/best_practices/',
      url: 'https://reddit.com/r/python/comments/def456/',
      upvotes: 89,
      comments: 23,
      score: 89,
      status: 'pending',
      assigned_to: null,
      created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      created_utc: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      fetched_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 3,
      reddit_post_id: 'ghi789',
      subreddit: 'reactjs',
      title: 'React hooks performance tips?',
      body: 'Are there any performance tips for using React hooks?',
      author: 'react_fan',
      permalink: '/r/reactjs/comments/ghi789/react_hooks/',
      url: 'https://reddit.com/r/reactjs/comments/ghi789/',
      upvotes: 156,
      comments: 67,
      score: 156,
      status: 'pending',
      assigned_to: null,
      created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      created_utc: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      fetched_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 4,
      reddit_post_id: 'jkl012',
      subreddit: 'webdev',
      title: 'Tailwind CSS vs styled-components?',
      body: 'Which do you prefer for styling React apps?',
      author: 'css_expert',
      permalink: '/r/webdev/comments/jkl012/tailwind_vs_styled/',
      url: 'https://reddit.com/r/webdev/comments/jkl012/',
      upvotes: 234,
      comments: 89,
      score: 234,
      status: 'pending',
      assigned_to: null,
      created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      created_utc: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      fetched_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 5,
      reddit_post_id: 'mno345',
      subreddit: 'python',
      title: 'SQLAlchemy ORM best practices?',
      body: 'What are the best practices for using SQLAlchemy ORM?',
      author: 'db_admin',
      permalink: '/r/python/comments/mno345/sqlalchemy_orm/',
      url: 'https://reddit.com/r/python/comments/mno345/',
      upvotes: 67,
      comments: 12,
      score: 67,
      status: 'pending',
      assigned_to: null,
      created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      created_utc: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      fetched_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    },
  ]
}





