"""
API URL configuration for worker dashboard.
"""
from django.urls import path
from src.api.views import (
    PendingPostsView,
    AssignPostView,
    MarkRepliedView,
    PostCommentView,
)

app_name = 'api'

urlpatterns = [
    path('posts/pending/', PendingPostsView.as_view(), name='pending-posts'),
    path('posts/assign/', AssignPostView.as_view(), name='assign-post'),
    path('posts/mark-replied/', MarkRepliedView.as_view(), name='mark-replied'),
    path('posts/comment/', PostCommentView.as_view(), name='post-comment'),
]

