"""
Filter to exclude advertisements and only keep high-intent posts.

High-intent posts are from people wanting to buy homes, not companies selling services.
"""
from typing import List, Dict, Any
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Company/advertisement indicators to exclude
AD_INDICATORS = [
    'real estate agent',
    'realtor',
    'real estate company',
    'mortgage broker',
    'lender',
    'for sale by owner',
    'fsbo',
    'listing',
    'open house',
    'contact us',
    'call now',
    'visit our website',
    'www.',
    'http://',
    'https://',
    '.com',
    '.net',
    '.org',
    'email',
    '@',
    'dm me',
    'message me',
    'reach out',
    'professional',
    'licensed',
    'certified',
    'years of experience',
    'specializing in',
    'services',
    'we help',
    'we offer',
    'our team',
    'our company',
]

# High-intent phrases that indicate someone wants to buy a home
HIGH_INTENT_PHRASES = [
    'buy a house',
    'buying a house',
    'buy home',
    'buy property',
    'first time home buyer',
    'first-time homebuyer',
    'preapproval',
    'pre-approval',
    'down payment',
    'making an offer',
    'bidding war',
    'mortgage rates',
    'closing costs',
    'home inspection',
    'contingencies',
    'should i rent or buy',
    'rent vs buy',
    'moving to',
    'relocating to',
    'thinking of moving',
    'considering moving',
    'planning to move',
    'is it worth buying',
    'can i afford',
    'how much house',
    'what is it like living',
    'any advice',
    'help me decide',
    'need help',
    'looking for',
    'want to buy',
    'trying to buy',
]


class IntentFilter:
    """
    Filters posts to exclude advertisements and only keep high-intent posts.
    
    High-intent posts are from people wanting to buy homes, not companies selling services.
    """
    
    def __init__(self):
        """Initialize the intent filter"""
        logger.info("IntentFilter initialized")
    
    def is_advertisement(self, post: Dict[str, Any]) -> bool:
        """
        Check if post is a company advertisement.
        
        Args:
            post: Normalized post dictionary
            
        Returns:
            True if post appears to be an advertisement
        """
        title = (post.get('title') or '').lower()
        body = (post.get('body') or '').lower()
        author = (post.get('author') or '').lower()
        combined_text = f"{title} {body} {author}"
        
        # Check for advertisement indicators
        for indicator in AD_INDICATORS:
            if indicator in combined_text:
                logger.debug(f"Post {post.get('post_id')} flagged as ad (indicator: {indicator})")
                return True
        
        # Check if author name looks like a company/business
        if any(word in author for word in ['realty', 'properties', 'homes', 'estate', 'group', 'team', 'llc', 'inc']):
            logger.debug(f"Post {post.get('post_id')} flagged as ad (author: {author})")
            return True
        
        return False
    
    def is_high_intent(self, post: Dict[str, Any]) -> bool:
        """
        Check if post indicates high intent (person wanting to buy home).
        
        Args:
            post: Normalized post dictionary
            
        Returns:
            True if post indicates high intent
        """
        title = (post.get('title') or '').lower()
        body = (post.get('body') or '').lower()
        combined_text = f"{title} {body}"
        
        # Check for high-intent phrases
        for phrase in HIGH_INTENT_PHRASES:
            if phrase in combined_text:
                logger.debug(f"Post {post.get('post_id')} flagged as high intent (phrase: {phrase})")
                return True
        
        return False
    
    def matches(self, post: Dict[str, Any]) -> bool:
        """
        Check if post should be kept (not an ad, high intent preferred but not required).
        
        Args:
            post: Normalized post dictionary
            
        Returns:
            True if post should be kept (only excludes ads)
        """
        # Exclude advertisements only
        if self.is_advertisement(post):
            return False
        
        # Keep all posts that aren't ads (high-intent check is informational only)
        # This allows more posts through while still filtering out company advertisements
        return True
    
    def filter_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of posts by intent.
        Only excludes advertisements - keeps all other posts.
        
        Args:
            posts: List of normalized post dictionaries
            
        Returns:
            Filtered list of non-advertisement posts (all posts except ads)
        """
        filtered = []
        ads_removed = 0
        high_intent_count = 0
        
        for post in posts:
            if self.is_advertisement(post):
                ads_removed += 1
                continue
            
            # Track high-intent for logging, but don't filter by it
            if self.is_high_intent(post):
                high_intent_count += 1
            
            filtered.append(post)
        
        logger.info(
            f"Intent filter: {len(filtered)}/{len(posts)} posts kept "
            f"({ads_removed} ads removed, {high_intent_count} high-intent posts)"
        )
        return filtered

