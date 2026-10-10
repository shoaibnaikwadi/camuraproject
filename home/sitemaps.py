
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

from .models import Product, JobOpening


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "about",
            "contact",
            "login",
            "register",
            "accessories",
            "privacy_policy",
            "shipping_policy",
            "warranty",
            "terms_and_conditions",
            "refund_cancellation_policy",
            "careers",
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        # Include active products only
        return Product.objects.filter(is_active=True)

    def location(self, obj):
        return reverse(
            "product_detail",
            args=[obj.pk],
        )

    def lastmod(self, obj):
        # Use updated_at when the model provides it
        return getattr(obj, "updated_at", None)


class JobOpeningSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return (
            JobOpening.objects
            .filter(is_active=True)
            .filter(
                Q(last_date__isnull=True)
                | Q(last_date__gte=timezone.localdate())
            )
        )

    def location(self, obj):
        return reverse(
            "job_detail",
            args=[obj.pk],
        )

    def lastmod(self, obj):
        return obj.created_at
