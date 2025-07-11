from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import BlogPost, BlogLike, BlogComment
from .forms import BlogPostForm
from authentication.models import Profile
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .ai_utils import generate_caption_and_hashtags

import logging

logger = logging.getLogger(__name__)


class BlogListCreateView(View):
    def get(self, request):
        blogs = BlogPost.objects.filter(active_status=True).order_by('-created_at')
        form = BlogPostForm()
        return render(request, "blog/blog_list.html", {"blogs": blogs, "form": form})

   def post(self, request):
    if not request.user.is_authenticated:
        return redirect("login")

    form = BlogPostForm(request.POST, request.FILES)
    if form.is_valid():
        blog = form.save(commit=False)
        blog.author = request.user.profile  # Ensure you're using Profile

        if blog.image:
            try:
                caption, hashtags = generate_caption_and_hashtags(blog.image.path)
                logger.info(f"[AI Captioning] Caption: {caption}")
                logger.info(f"[AI Captioning] Hashtags: {hashtags}")
                blog.caption = caption
                blog.hashtags = ", ".join(hashtags)

                # Use AI caption as title if not manually given
                if not blog.title:
                    blog.title = caption
            except Exception as e:
                logger.error(f"[AI Captioning] Failed: {e}")
                if not blog.title:
                    blog.title = "Untitled"

        # Ensure there's always a title
        if not blog.title:
            blog.title = "Untitled"

        blog.save()
        return redirect("blog-list")

    # If form is invalid, re-render with errors
    blogs = BlogPost.objects.filter(active_status=True).order_by('-created_at')
    return render(request, "blog/blog_list.html", {"blogs": blogs, "form": form})

@method_decorator(login_required, name='dispatch')
class BlogLikeToggleView(View):
    def post(self, request, blog_id):
        blog = get_object_or_404(BlogPost, id=blog_id)
        user_profile = request.user  # You can replace with `.profile` if your likes use Profile

        like, created = BlogLike.objects.get_or_create(post=blog, user=user_profile)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'liked': liked,
                'total_likes': blog.total_likes(),
                'blog_id': blog.id
            })

        return redirect(request.META.get("HTTP_REFERER", "blog-list"))


@method_decorator(login_required, name='dispatch')
class AddCommentView(View):
    def post(self, request, blog_id):
        blog = get_object_or_404(BlogPost, id=blog_id)
        comment_text = request.POST.get("comment", "").strip()

        if comment_text:
            BlogComment.objects.create(
                post=blog,
                user=request.user,  # replace with `request.user.profile` if needed
                comment=comment_text
            )

        return redirect(request.META.get("HTTP_REFERER", "blog-list"))


@method_decorator(login_required, name='dispatch')
class DeleteBlogPostView(View):
    def post(self, request, pk):
        blog = get_object_or_404(BlogPost, pk=pk)
        if blog.author.user == request.user:
            blog.delete()
        return redirect('blog-list')


@method_decorator(login_required, name='dispatch')
class DeleteBlogCommentView(View):
    def post(self, request, pk):
        comment = get_object_or_404(BlogComment, pk=pk)
        if comment.user.user == request.user:
            comment.delete()
        return redirect(request.META.get('HTTP_REFERER', 'blog-list'))
