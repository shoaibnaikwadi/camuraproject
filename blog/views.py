from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Category



import json


def blog_list(request):
    """
    Blog listing page.

    Provides:
    - All blog posts
    - Categories
    - Featured posts
    - ItemList structured data
    """

    posts = BlogPost.objects.order_by("-created_at")

    categories = Category.objects.all()

    featured = BlogPost.objects.filter(
        featured=True
    )[:3]

    # ----------------------------------------
    # ItemList Structured Data
    # ----------------------------------------

    item_list = []

    for position, post in enumerate(posts, start=1):

        article_url = (
            f"https://camura.in{post.get_absolute_url()}"
        )

        item_list.append({
            "@type": "ListItem",
            "position": position,
            "url": article_url,
            "name": post.title,
        })

    blog_list_schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Camura Blog Articles",
        "url": "https://camura.in/blog/",
        "numberOfItems": len(item_list),
        "itemListElement": item_list,
    }

    # Convert Python dictionary to JSON
    blog_list_schema = json.dumps(
        blog_list_schema,
        ensure_ascii=False
    )

    return render(
        request,
        "blog/blog_list.html",
        {
            "posts": posts,
            "categories": categories,
            "featured": featured,
            "blog_list_schema": blog_list_schema,
        }
    )


def blog_detail(request, slug):
    """
    Individual blog article page.

    Provides:
    - Blog post
    - Tags
    - BlogPosting structured data
    """

    post = get_object_or_404(
        BlogPost,
        slug=slug
    )

    # ----------------------------------------
    # Tags
    # ----------------------------------------

    tags = []

    if post.tags:
        tags = [
            tag.strip()
            for tag in post.tags.split(",")
            if tag.strip()
        ]

    # ----------------------------------------
    # Article URL
    # ----------------------------------------

    article_url = (
        f"https://camura.in{post.get_absolute_url()}"
    )

    # ----------------------------------------
    # Description
    # ----------------------------------------

    description = (
        post.meta_description
        or post.short_description
        or ""
    )

    # ----------------------------------------
    # BlogPosting Structured Data
    # ----------------------------------------

    blog_schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",

        "@id": f"{article_url}#article",

        "url": article_url,

        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": article_url,
        },

        "headline": post.title,

        "description": description,

        # ------------------------------------
        # Author
        # ------------------------------------

        "author": {
            "@type": "Organization",
            "@id": "https://camura.in/#organization",
            "name": "Camura",
            "url": "https://camura.in/",
        },

        # ------------------------------------
        # Publisher
        # ------------------------------------

        "publisher": {
            "@type": "Organization",
            "@id": "https://camura.in/#organization",
            "name": "Camura",
            "legalName": "N S Corporation",
            "url": "https://camura.in/",
            "logo": {
                "@type": "ImageObject",
                "url": (
                    "https://camura.in"
                    "/static/img/camura_logo.png"
                ),
            },
        },

        # ------------------------------------
        # Dates
        # ------------------------------------

        "datePublished": post.created_at.isoformat(),

        "dateModified": (
            post.updated_at
            or post.created_at
        ).isoformat(),
    }

    # ----------------------------------------
    # Featured Image
    # ----------------------------------------

    if post.featured_image:

        blog_schema["image"] = [
            f"https://camura.in{post.featured_image.url}"
        ]

    # ----------------------------------------
    # Keywords / Tags
    # ----------------------------------------

    if tags:
        blog_schema["keywords"] = tags

    # ----------------------------------------
    # Convert Schema to JSON
    # ----------------------------------------

    blog_schema = json.dumps(
        blog_schema,
        ensure_ascii=False
    )

    # ----------------------------------------
    # Render
    # ----------------------------------------

    return render(
        request,
        "blog/blog_detail.html",
        {
            "post": post,
            "tags": tags,
            "blog_schema": blog_schema,
        }
    )

# def blog_list(request):
#     posts = BlogPost.objects.order_by('-created_at')
#     categories = Category.objects.all()
#     featured = BlogPost.objects.filter(featured=True)[:3]
#     return render(request, "blog/blog_list.html", {
#         "posts": posts,
#         "categories": categories,
#         "featured": featured,
#     })






# def blog_detail(request, slug):
#     post = get_object_or_404(BlogPost, slug=slug)

#     tags = []
#     if post.tags:
#         tags = [t.strip() for t in post.tags.split(",")]

#     return render(request, "blog/blog_detail.html", {
#         "post": post,
#         "tags": tags,
#     })






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
