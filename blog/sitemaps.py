from django.contrib.sitemaps import Sitemap
from .models import BlogPost

class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return BlogPost.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
