"""
Custom exceptions for the crawler system.
"""


class CrawlerException(Exception):
    """Base exception for crawler errors"""
    pass


class RedditAPIException(CrawlerException):
    """Reddit API related errors"""
    pass


class FilterException(CrawlerException):
    """Filtering related errors"""
    pass


class StorageException(CrawlerException):
    """Storage related errors"""
    pass


class DeduplicationException(CrawlerException):
    """Deduplication related errors"""
    pass


class CommentPostingException(CrawlerException):
    """Comment posting related errors"""
    pass

