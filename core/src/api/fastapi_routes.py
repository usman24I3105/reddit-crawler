"""
FastAPI routes for worker dashboard.
Clean REST API matching the requirements.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db.repository import PostRepository
from src.db.session import get_db
from src.db.models import Post, Comment
from src.reddit.commenter import RedditCommenter
from src.reddit.fetcher import RedditFetcher
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])
security = HTTPBearer()


# Pydantic models for request/response
class PostResponse(BaseModel):
    """Post response model"""
    id: int
    reddit_post_id: Optional[str]
    subreddit: str
    title: str
    body: Optional[str]
    author: str
    permalink: Optional[str]
    url: Optional[str]
    reddit_url: Optional[str]
    upvotes: int
    comments: int
    score: int
    status: str
    assigned_to: Optional[str]
    created_at: str
    created_utc: Optional[str]
    fetched_at: str

    class Config:
        from_attributes = True


class AssignRequest(BaseModel):
    """Request model for assigning a post"""
    worker_id: str


class ReplyRequest(BaseModel):
    """Request model for replying to a post"""
    comment_text: str
    worker_id: str


class CommentResponse(BaseModel):
    """Comment response model"""
    id: int
    reddit_comment_id: Optional[str]
    post_id: int
    reddit_post_id: str
    body: Optional[str]
    author: str
    upvotes: int
    score: int
    permalink: Optional[str]
    reddit_url: Optional[str]
    created_utc: Optional[str]
    fetched_at: str

    class Config:
        from_attributes = True


# Simple auth dependency (placeholder - implement JWT in production)
async def get_current_worker(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated worker.
    TODO: Implement JWT token validation
    """
    # For now, just return the token as worker_id
    # In production, decode JWT and extract user info
    token = credentials.credentials
    return token  # Placeholder


@router.get("", response_model=List[PostResponse])
async def get_posts(
    status: Optional[str] = Query(None, description="Filter by status (pending, in_progress, replied)"),
    subreddit: Optional[str] = Query(None, description="Filter by subreddit"),
    limit: Optional[int] = Query(None, ge=1, description="Maximum number of posts (default: no limit)"),
    db: Session = Depends(get_db)
    # Note: Authentication removed for easier testing - add back in production
):
    """
    Get posts with optional filtering.
    No limit by default - returns all matching posts.
    
    Matches requirement: GET /posts?status=pending
    """
    repository = PostRepository(db)
    
    try:
        if status == 'pending':
            posts = repository.get_pending_posts(limit=limit, subreddit=subreddit)
        elif status:
            # Query by specific status
            from src.db.models import Post
            query = db.query(Post).filter(Post.status == status)
            if subreddit:
                query = query.filter(Post.subreddit == subreddit)
            query = query.order_by(Post.fetched_at.desc())
            if limit:
                query = query.limit(limit)
            posts = query.all()
        else:
            # No status filter - return all posts (no limit by default)
            from src.db.models import Post
            query = db.query(Post)
            if subreddit:
                query = query.filter(Post.subreddit == subreddit)
            query = query.order_by(Post.fetched_at.desc())
            if limit:
                query = query.limit(limit)
            posts = query.all()
        
        # Convert posts to response format
        result = []
        for post in posts:
            post_dict = post.to_dict()
            result.append(PostResponse(**post_dict))
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving posts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve posts: {str(e)}"
        )


@router.post("/{post_id}/assign", status_code=status.HTTP_200_OK)
async def assign_post(
    post_id: str,
    request: AssignRequest,
    db: Session = Depends(get_db),
    worker_id: str = Depends(get_current_worker)
):
    """
    Assign a post to a worker.
    
    Matches requirement: POST /posts/{id}/assign
    """
    repository = PostRepository(db)
    
    try:
        # Use worker_id from request or token
        assigned_to = request.worker_id or worker_id
        
        success = repository.assign_post(post_id, assigned_to)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or already assigned"
            )
        
        logger.info(f"Post {post_id} assigned to {assigned_to}")
        return {
            "message": "Post assigned successfully",
            "post_id": post_id,
            "assigned_to": assigned_to
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning post: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign post: {str(e)}"
        )


@router.post("/{post_id}/reply", status_code=status.HTTP_200_OK)
async def reply_to_post(
    post_id: str,
    request: ReplyRequest,
    db: Session = Depends(get_db),
    worker_id: str = Depends(get_current_worker)
):
    """
    Reply to a Reddit post and mark it as replied.
    
    Matches requirement: POST /posts/{id}/reply
    """
    repository = PostRepository(db)
    
    try:
        # Verify post is assigned to this worker
        post = repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        worker = request.worker_id or worker_id
        if post.assigned_to != worker:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Post is not assigned to you"
            )
        
        # Post comment using RedditCommenter
        commenter = RedditCommenter()
        comment = commenter.post_comment(post_id, request.comment_text)
        
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to post comment. Check server logs for details."
            )
        
        # Mark post as replied
        repository.mark_replied(post_id, worker)
        
        logger.info(f"Comment posted to post {post_id} by {worker}")
        return {
            "message": "Comment posted successfully",
            "post_id": post_id,
            "comment_id": comment.id if comment else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error posting comment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post comment: {str(e)}"
        )


@router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments(
    post_id: str,
    limit: Optional[int] = Query(50, ge=1, le=200, description="Maximum number of comments"),
    fetch_from_reddit: bool = Query(False, description="Fetch fresh comments from Reddit"),
    db: Session = Depends(get_db)
):
    """
    Get comments for a specific post.
    Can fetch from database or fetch fresh from Reddit.
    
    Matches requirement: GET /posts/{id}/comments
    """
    repository = PostRepository(db)
    
    try:
        # Verify post exists
        post = repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        comments = []
        
        if fetch_from_reddit:
            # Fetch fresh comments from Reddit
            logger.info(f"Fetching fresh comments from Reddit for post {post_id}")
            fetcher = RedditFetcher()
            reddit_comments = fetcher.fetch_comments_for_post(post_id, limit=limit)
            
            # Save comments to database
            for comment_data in reddit_comments:
                comment_data['reddit_post_id'] = post_id
                try:
                    comment = repository.create_comment(comment_data)
                    comments.append(comment)
                except Exception as e:
                    logger.warning(f"Failed to save comment: {str(e)}")
                    # Still add to response even if save failed
                    # Convert dict to Comment-like object for response
                    comment_dict = comment_data.copy()
                    comment_dict['id'] = 0
                    comment_dict['post_id'] = post.id
                    comments.append(comment_dict)
        else:
            # Get comments from database
            comments = repository.get_comments_for_post(post_id, limit=limit)
        
        # Convert to response format
        result = []
        for comment in comments:
            if isinstance(comment, dict):
                # Already a dict from Reddit fetch
                reddit_url = None
                if comment.get('permalink'):
                    permalink = comment['permalink']
                    if permalink.startswith('http'):
                        reddit_url = permalink
                    else:
                        reddit_url = f"https://reddit.com{permalink}"
                
                result.append(CommentResponse(
                    id=comment.get('id', 0),
                    reddit_comment_id=comment.get('comment_id'),
                    post_id=comment.get('post_id', post.id),
                    reddit_post_id=post_id,
                    body=comment.get('body'),
                    author=comment.get('author', '[deleted]'),
                    upvotes=comment.get('upvotes', 0),
                    score=comment.get('score', 0),
                    permalink=comment.get('permalink'),
                    reddit_url=reddit_url,
                    created_utc=comment.get('created_utc').isoformat() if comment.get('created_utc') else None,
                    fetched_at=comment.get('fetched_at').isoformat() if comment.get('fetched_at') else None,
                ))
            else:
                # Comment model instance
                comment_dict = comment.to_dict()
                result.append(CommentResponse(**comment_dict))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving comments: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve comments: {str(e)}"
        )

