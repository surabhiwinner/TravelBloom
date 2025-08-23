from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from .models import BlogPost, BlogLike, BlogComment
from .forms import BlogPostForm


class BlogListCreateView(View):
    """
    Handles listing all active blog posts and creating a new blog post.
    """
    def get(self, request):
        blogs = BlogPost.objects.filter(active_status=True).order_by('-created_at')
        form = BlogPostForm()
        return render(
            request,
            "blog/blog_list.html",
            {"blogs": blogs, "form": form, "page": "blog-page"}
        )

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user

            # Ensure fallback title
            if not blog.title:
                blog.title = "Untitled"

            blog.save()
            return redirect("blog-list")

        blogs = BlogPost.objects.filter(active_status=True).order_by('-created_at')
        return render(
            request,
            "blog/blog_list.html",
            {"blogs": blogs, "form": form}
        )


@method_decorator(login_required, name='dispatch')
class BlogLikeToggleView(View):
    """
    Handles liking/unliking a blog post (AJAX + fallback redirect).
    """
    def post(self, request, blog_id):
        blog = get_object_or_404(BlogPost, id=blog_id)
        user_profile = request.user  # or request.user.profile if tied to Profile

        like, created = BlogLike.objects.get_or_create(post=blog, user=user_profile)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "liked": liked,
                "total_likes": blog.total_likes(),
                "blog_id": blog.id
            })

        return redirect(request.META.get("HTTP_REFERER", "blog-list"))


@method_decorator(login_required, name='dispatch')
class AddCommentView(View):
    """
    Handles adding a comment to a blog post.
    """
    def post(self, request, blog_id):
        blog = get_object_or_404(BlogPost, id=blog_id)
        comment_text = request.POST.get("comment", "").strip()

        if comment_text:
            BlogComment.objects.create(
                post=blog,
                user=request.user,  # or request.user.profile
                comment=comment_text
            )

        return redirect(request.META.get("HTTP_REFERER", "blog-list"))


@method_decorator(login_required, name='dispatch')
class DeleteBlogCommentView(View):
    """
    Handles deleting a comment if authorized.
    """
    def post(self, request, pk):
        comment = get_object_or_404(BlogComment, pk=pk)

        if comment.user == request.user or request.user.is_superuser:
            comment.delete()
            messages.success(request, "Comment deleted successfully.")
        else:
            messages.error(request, "You're not authorized to delete this comment.")

        return redirect(request.META.get("HTTP_REFERER", "blog-list"))


@method_decorator(login_required, name='dispatch')
class DeleteBlogPostView(View):
    """
    Handles deleting a blog post if authorized.
    """
    def post(self, request, pk):
        blog = get_object_or_404(BlogPost, pk=pk)

        if request.user == blog.author or request.user.is_superuser:
            blog.delete()
            messages.success(request, "Blog post deleted successfully.")
        else:
            messages.error(request, "You are not authorized to delete this blog post.")

        return redirect("blog-list")
