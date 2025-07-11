from django.urls import path
from . import views
from .views import BlogLikeToggleView,AddCommentView
urlpatterns = [
    path('blog-list/', views.BlogListCreateView.as_view(), name='blog-list'),
    path('like/<int:blog_id>/', BlogLikeToggleView.as_view(), name='blog-like-toggle'),

    path('comment/<int:blog_id>/', AddCommentView.as_view(), name='add-blog-comment'),
    path('delete/post/<int:pk>/', views.DeleteBlogPostView.as_view(), name='delete-blog-post'),
    path('delete/comment/<int:pk>/', views.DeleteBlogCommentView.as_view(), name='delete-blog-comment'),

    ]