from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Category

def blog_list(request):
    posts = BlogPost.objects.order_by('-created_at')
    categories = Category.objects.all()
    featured = BlogPost.objects.filter(featured=True)[:3]
    return render(request, "blog/blog_list.html", {
        "posts": posts,
        "categories": categories,
        "featured": featured,
    })



def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    related_posts = BlogPost.objects.filter(
        category=post.category
    ).exclude(id=post.id)[:3]

    return render(request, "blog/blog_detail.html", {
        "post": post,
        "related_posts": related_posts,
    })



def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(category=category).order_by('-created_at')
    return render(request, "blog/category_posts.html", {
        "category": category,
        "posts": posts
    })


def blog_search(request):
    query = request.GET.get("q", "")
    posts = BlogPost.objects.filter(title__icontains=query)
    return render(request, "blog/blog_search.html", {
        "query": query,
        "posts": posts
    })
