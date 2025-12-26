"""
Worker dashboard API views.
Updated to use SQLAlchemy repository pattern with lifecycle management.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from src.db.repository import PostRepository
from src.db.session import SessionLocal
from src.lifecycle import ActionValidator, PostAction, ActionException
from src.lifecycle import LifecycleException
from src.reddit.commenter import RedditCommenter
from src.utils.logging import get_logger

logger = get_logger(__name__)


def get_repository() -> PostRepository:
    """Get database repository instance"""
    db = SessionLocal()
    return PostRepository(db)


class PendingPostsView(APIView):
    """Get pending posts for worker dashboard"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """
        Get pending posts.
        
        Query params:
            limit: Maximum number of posts to return (default: 50)
            subreddit: Filter by subreddit (optional)
        """
        db = SessionLocal()
        try:
            limit = int(request.query_params.get('limit', 50))
            subreddit = request.query_params.get('subreddit')
            
            repository = PostRepository(db)
            posts = repository.get_pending_posts(limit=limit, subreddit=subreddit)
            
            # Convert to dict format (matching old API response)
            data = []
            for post in posts:
                data.append({
                    'post_id': post.reddit_post_id,
                    'subreddit': post.subreddit,
                    'title': post.title,
                    'body': post.body,
                    'author': post.author,
                    'permalink': post.permalink,
                    'url': post.url,
                    'upvotes': post.upvotes,
                    'num_comments': post.comments,  # Map comments field
                    'score': post.score,
                    'created_utc': post.created_utc.isoformat() if post.created_utc else None,
                    'fetched_at': post.fetched_at.isoformat() if post.fetched_at else None,
                    'status': post.status,
                    'assigned_to': post.assigned_to,
                })
            
            logger.info(f"Retrieved {len(data)} pending posts for user {request.user.username}")
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving pending posts: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to retrieve pending posts'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            db.close()


class AssignPostView(APIView):
    """Assign a post to a worker"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        """
        Assign a post to the current user.
        
        Validates action is allowed for post status (pending → assigned).
        
        Body:
            post_id: Reddit post ID
        """
        db = SessionLocal()
        try:
            post_id = request.data.get('post_id')
            if not post_id:
                return Response(
                    {'error': 'post_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            repository = PostRepository(db)
            post = repository.get_post_by_id(post_id)
            
            if not post:
                return Response(
                    {'error': 'Post not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate action is allowed
            try:
                ActionValidator.validate_action(
                    post=post,
                    action=PostAction.ASSIGN_TO_WORKER,
                    user=request.user.username
                )
            except ActionException as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Assign post (lifecycle service validates transition)
            try:
                success = repository.assign_post(post_id, request.user.username)
                
                if not success:
                    return Response(
                        {'error': 'Failed to assign post'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                logger.info(f"Post {post_id} assigned to {request.user.username}")
                return Response(
                    {'message': 'Post assigned successfully', 'post_id': post_id},
                    status=status.HTTP_200_OK
                )
            except LifecycleException as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            logger.error(f"Error assigning post: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to assign post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            db.close()


class MarkRepliedView(APIView):
    """Mark a post as replied (after posting comment)"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        """
        Mark a post as replied (assigned → replied).
        
        Validates action is allowed and post is assigned to current user.
        
        Body:
            post_id: Reddit post ID
            comment_text: Optional comment text that was posted
        """
        db = SessionLocal()
        try:
            post_id = request.data.get('post_id')
            if not post_id:
                return Response(
                    {'error': 'post_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            repository = PostRepository(db)
            
            # Get post
            post = repository.get_post_by_id(post_id)
            if not post:
                return Response(
                    {'error': 'Post not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate action is allowed
            try:
                ActionValidator.validate_action(
                    post=post,
                    action=PostAction.REPLY,
                    user=request.user.username
                )
            except ActionException as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Mark as replied (lifecycle service validates transition)
            try:
                success = repository.mark_replied(post_id, request.user.username)
                
                if not success:
                    return Response(
                        {'error': 'Failed to update post status'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                logger.info(f"Post {post_id} marked as replied by {request.user.username}")
                return Response(
                    {'message': 'Post marked as replied', 'post_id': post_id},
                    status=status.HTTP_200_OK
                )
            except LifecycleException as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            logger.error(f"Error marking post as replied: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to mark post as replied'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            db.close()


class PostCommentView(APIView):
    """Post a comment to a Reddit post"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        """
        Post a comment to a Reddit post (assigned → replied).
        
        Validates action is allowed and post is assigned to current user.
        Automatically transitions post to 'replied' status after successful comment.
        
        Body:
            post_id: Reddit post ID
            comment_text: Text of the comment to post
        """
        db = SessionLocal()
        try:
            post_id = request.data.get('post_id')
            comment_text = request.data.get('comment_text')
            
            if not post_id or not comment_text:
                return Response(
                    {'error': 'post_id and comment_text are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            repository = PostRepository(db)
            
            # Get post
            post = repository.get_post_by_id(post_id)
            if not post:
                return Response(
                    {'error': 'Post not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate action is allowed
            try:
                ActionValidator.validate_action(
                    post=post,
                    action=PostAction.REPLY,
                    user=request.user.username
                )
            except ActionException as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Post comment using RedditCommenter
            commenter = RedditCommenter()
            comment = commenter.post_comment(post_id, comment_text)
            
            if not comment:
                return Response(
                    {'error': 'Failed to post comment. Check server logs for details.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Mark post as replied (lifecycle service validates transition)
            try:
                repository.mark_replied(post_id, request.user.username)
            except LifecycleException as e:
                logger.warning(f"Failed to mark post as replied after comment: {str(e)}")
                # Comment was posted, but status update failed - log warning but don't fail
            
            logger.info(f"Comment posted to post {post_id} by {request.user.username}")
            return Response(
                {
                    'message': 'Comment posted successfully',
                    'post_id': post_id,
                    'comment_id': comment.id if comment else None
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error posting comment: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to post comment: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            db.close()

