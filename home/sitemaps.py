from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product  # adjust model name if different


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            'index',
            'about',
            'contact',
            'cart',
            'checkout',
            'login',
            'register',
            'privacy_policy',
            'terms_and_conditions',
            'refund_cancellation_policy',
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None
