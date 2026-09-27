from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import BlogPost


class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return BlogPost.objects.all()

    def location(self, obj):
        return reverse(
            "blog_detail",
            kwargs={"slug": obj.slug}
        )

    def lastmod(self, obj):
        return obj.updated_at