from django.db import models
from django.utils import timezone


class SubredditPost(models.Model):
    """Reddit post model with full support for worker dashboard"""
    
    # Post identification (for deduplication)
    post_id = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True, help_text="Reddit post ID")
    permalink = models.CharField(max_length=500, blank=True, db_index=True, help_text="Reddit permalink")
    
    # Basic post information
    subreddit = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True, help_text="Post body/selftext")
    author = models.CharField(max_length=100, default='[deleted]')
    url = models.URLField(max_length=500, blank=True)
    
    # Engagement metrics
    upvotes = models.IntegerField(default=0, help_text="Number of upvotes")
    num_comments = models.IntegerField(default=0, help_text="Number of comments")
    score = models.IntegerField(default=0, help_text="Reddit score")
    
    # Timestamps
    created_utc = models.DateTimeField(help_text="Post creation time (UTC)")
    fetched_at = models.DateTimeField(default=timezone.now, db_index=True, help_text="When we fetched this post")
    
    # Worker dashboard fields
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('replied', 'Replied'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Post processing status"
    )
    assigned_to = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text="Worker assigned to this post"
    )
    
    class Meta:
        ordering = ['-fetched_at']
        indexes = [
            models.Index(fields=['status', '-fetched_at']),
            models.Index(fields=['subreddit', '-fetched_at']),
        ]
    
    def __str__(self):
        return f"{self.subreddit}: {self.title[:50]}"
