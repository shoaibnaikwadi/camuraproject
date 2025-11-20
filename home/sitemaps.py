from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import ComboProduct  


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            'home',
            'about',
            'contact',
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
        return ComboProduct.objects.all()

    def location(self, obj):
        return reverse('product_detail', args=[obj.pk])

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None
