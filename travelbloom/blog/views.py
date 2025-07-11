from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import BlogPost, BlogLike,BlogComment
from .forms import BlogPostForm
from authentication.models import Profile
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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
            blog.author = request.user.profile  # Assuming you use Profile
            blog.save()
            return redirect("blog-list")

        blogs = BlogPost.objects.filter(active_status=True).order_by('-created_at')
        return render(request, "blog/blog_list.html", {"blogs": blogs, "form": form})






class BlogLikeToggleView(View):
    @method_decorator(login_required)
    def post(self, request, blog_id):
        blog = get_object_or_404(BlogPost, id=blog_id)
        user = request.user
        like, created = BlogLike.objects.get_or_create(post=blog, user=user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            'liked': liked,
            'total_likes': blog.likes.count(),
        })

    def post(self, request, blog_id):
        blog = get_object_or_404(BlogPost, id=blog_id)
        user_profile = request.user  # assume it's the Profile

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
                post=blog,  # ✅ use `post`, not `blog`
                user=request.user,  # ✅ assuming `Profile` is linked to user
                comment=comment_text
            )

        return redirect(request.META.get("HTTP_REFERER", "blog-list"))
    
class DeleteBlogPostView( View):
    def post(self, request, pk):
        blog = get_object_or_404(BlogPost, pk=pk)
        if blog.author.user == request.user:  # assuming blog.author is a Profile
            blog.delete()
        return redirect('blog-list')


class DeleteBlogCommentView( View):
    def post(self, request, pk):
        comment = get_object_or_404(BlogComment, pk=pk)
        if comment.user.user == request.user:  # assuming comment.user is a Profile
            comment.delete()
        return redirect(request.META.get('HTTP_REFERER', 'blog-list'))

