from django.views import View
from django.shortcuts import render, redirect
from .models import BlogPost
from .forms import BlogPostForm

class BlogListCreateView(View):
    def get(self, request):
        blogs = BlogPost.objects.filter(active_status=True).order_by('-created_at')
        form = BlogPostForm()
        return render(request, "blogs/blog_list.html", {"blogs": blogs, "form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            
            # ✅ Set the correct user field
            blog.author = request.user # or `request.user` depending on your model
            
            blog.save()
            return redirect("blog-list")

        blogs = BlogPost.objects.filter(active_status=True).order_by('-created_at')
        return render(request, "blogs/blog_list.html", {"blogs": blogs, "form": form})
