"""
SQLAlchemy models for Reddit crawler.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Post(Base):
    """
    Reddit post model.
    
    Fields match the requirements:
    - reddit_post_id (UNIQUE) - for deduplication
    - subreddit, title, body, author, permalink
    - upvotes, comments, score
    - status (pending, in_progress, replied)
    - assigned_to (nullable)
    - created_at (timestamp)
    """
    __tablename__ = 'posts'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Post identification (for deduplication)
    reddit_post_id = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="Reddit post ID - UNIQUE constraint for deduplication"
    )
    permalink = Column(
        String(500),
        nullable=True,
        index=True,
        comment="Reddit permalink"
    )
    
    # Basic post information
    subreddit = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=True, comment="Post body/selftext")
    author = Column(String(100), nullable=False, default='[deleted]')
    url = Column(String(500), nullable=True, comment="Post URL")
    
    # Engagement metrics
    upvotes = Column(Integer, nullable=False, default=0, comment="Number of upvotes")
    comments = Column(Integer, nullable=False, default=0, comment="Number of comments")
    score = Column(Integer, nullable=False, default=0, comment="Reddit score")
    
    # Worker dashboard fields
    status = Column(
        String(20),
        nullable=False,
        default='fetched',
        index=True,
        comment="Post processing status: fetched, pending, assigned, replied, archived"
    )
    assigned_to = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Worker assigned to this post"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="When this record was created in our database"
    )
    created_utc = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Post creation time on Reddit (UTC)"
    )
    fetched_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="When we fetched this post from Reddit"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_status_fetched_at', 'status', 'fetched_at'),
        Index('idx_subreddit_fetched_at', 'subreddit', 'fetched_at'),
    )
    
    def __repr__(self):
        return f"<Post(id={self.id}, reddit_post_id={self.reddit_post_id}, subreddit={self.subreddit}, title={self.title[:50]})>"
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary"""
        # Build full Reddit URL from permalink
        reddit_url = None
        if self.permalink:
            if self.permalink.startswith('http'):
                reddit_url = self.permalink
            else:
                reddit_url = f"https://reddit.com{self.permalink}"
        
        return {
            'id': self.id,
            'reddit_post_id': self.reddit_post_id,
            'subreddit': self.subreddit,
            'title': self.title,
            'body': self.body,
            'author': self.author,
            'permalink': self.permalink,
            'url': self.url,
            'reddit_url': reddit_url,  # Full clickable URL
            'upvotes': self.upvotes,
            'comments': self.comments,
            'score': self.score,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_utc': self.created_utc.isoformat() if self.created_utc else None,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
        }


class Keyword(Base):
    """
    Keyword model for storing primary and secondary keywords.
    
    Supports scalable keyword matching with types:
    - primary: Intent keywords (e.g., "how to", "need help")
    - secondary: Domain/topic keywords (e.g., "fastapi", "react")
    
    Matching rule: Post is valid ONLY IF (at least 1 primary) AND (at least 1 secondary)
    """
    __tablename__ = 'keywords'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Keyword text (normalized to lowercase)
    word = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Keyword text (normalized to lowercase)"
    )
    
    # Keyword type: 'primary' or 'secondary'
    type = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Keyword type: primary (intent) or secondary (domain/topic)"
    )
    
    # Client identifier (for multi-tenant support)
    client_id = Column(
        String(100),
        nullable=True,
        index=True,
        default='default',
        comment="Client identifier for multi-tenant support"
    )
    
    # Enable/disable keyword
    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether this keyword is enabled for matching"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When this keyword was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="When this keyword was last updated"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_keyword_type_enabled', 'type', 'enabled'),
        Index('idx_keyword_client_enabled', 'client_id', 'enabled'),
        Index('idx_keyword_word_type', 'word', 'type'),
    )
    
    def __repr__(self):
        return f"<Keyword(id={self.id}, word={self.word}, type={self.type}, enabled={self.enabled})>"
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'word': self.word,
            'type': self.type,
            'client_id': self.client_id,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Comment(Base):
    """
    Reddit comment model.
    Stores comments fetched from Reddit posts.
    """
    __tablename__ = 'comments'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Comment identification
    reddit_comment_id = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="Reddit comment ID - UNIQUE constraint for deduplication"
    )
    
    # Post reference
    post_id = Column(
        Integer,
        ForeignKey('posts.id'),
        nullable=False,
        index=True,
        comment="Reference to posts.id"
    )
    reddit_post_id = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Reddit post ID for easy lookup"
    )
    
    # Comment content
    body = Column(Text, nullable=True, comment="Comment body/text")
    author = Column(String(100), nullable=False, default='[deleted]', comment="Comment author")
    
    # Engagement metrics
    upvotes = Column(Integer, nullable=False, default=0, comment="Number of upvotes")
    score = Column(Integer, nullable=False, default=0, comment="Reddit score")
    
    # Permalink for direct link to comment
    permalink = Column(
        String(500),
        nullable=True,
        comment="Reddit permalink to this comment"
    )
    
    # Timestamps
    created_utc = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Comment creation time on Reddit (UTC)"
    )
    fetched_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="When we fetched this comment from Reddit"
    )
    
    # Relationship to post
    post = relationship("Post", backref="post_comments")
    
    # Indexes
    __table_args__ = (
        Index('idx_comment_post_id', 'post_id', 'fetched_at'),
        Index('idx_comment_reddit_post', 'reddit_post_id', 'fetched_at'),
    )
    
    def __repr__(self):
        return f"<Comment(id={self.id}, reddit_comment_id={self.reddit_comment_id}, post_id={self.post_id})>"
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary"""
        # Build full Reddit URL from permalink
        reddit_url = None
        if self.permalink:
            if self.permalink.startswith('http'):
                reddit_url = self.permalink
            else:
                reddit_url = f"https://reddit.com{self.permalink}"
        
        return {
            'id': self.id,
            'reddit_comment_id': self.reddit_comment_id,
            'post_id': self.post_id,
            'reddit_post_id': self.reddit_post_id,
            'body': self.body,
            'author': self.author,
            'upvotes': self.upvotes,
            'score': self.score,
            'permalink': self.permalink,
            'reddit_url': reddit_url,  # Full clickable URL
            'created_utc': self.created_utc.isoformat() if self.created_utc else None,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
        }


class PostStatusLog(Base):
    """
    Log of all post status changes for audit trail.
    """
    __tablename__ = 'post_status_logs'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Post reference
    post_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Reference to posts.id"
    )
    reddit_post_id = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Reddit post ID for easy lookup"
    )
    
    # Status change information
    old_status = Column(
        String(20),
        nullable=True,
        comment="Previous status"
    )
    new_status = Column(
        String(20),
        nullable=False,
        comment="New status"
    )
    
    # Who/what made the change
    changed_by = Column(
        String(100),
        nullable=True,
        comment="User/system that made the change"
    )
    change_reason = Column(
        String(200),
        nullable=True,
        comment="Reason for status change (e.g., 'auto_expire', 'manual_assign')"
    )
    
    # Timestamp
    changed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="When the status change occurred"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_status_log_post', 'post_id', 'changed_at'),
        Index('idx_status_log_reddit_post', 'reddit_post_id', 'changed_at'),
    )
    
    def __repr__(self):
        return f"<PostStatusLog(id={self.id}, post_id={self.post_id}, {self.old_status} -> {self.new_status})>"
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'reddit_post_id': self.reddit_post_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by': self.changed_by,
            'change_reason': self.change_reason,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
        }




