
from django.contrib.sitemaps import Sitemap
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from .models import Product, JobOpening


# ============================================================
# STATIC PAGES
# ============================================================

class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"
    protocol = "https"


    def items(self):
        return [
            "home",
            "product_list",
            "accessories",
            "about",
            "contact",
            "privacy_policy",
            "shipping_policy",
            "warranty",
            "terms_and_conditions",
            "refund_cancellation_policy",
            "careers",
            "videos",
        ]

    def location(self, item):
        return reverse(item)


# ============================================================
# PRODUCTS AND CCTV COMBO KITS
# ============================================================

class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"
    protocol = "https"


    def items(self):
        return Product.objects.filter(
            is_active=True
        ).order_by("-updated_at")

    def location(self, obj):
        return reverse("product_detail", args=[obj.pk])

    def lastmod(self, obj):
        return getattr(obj, "updated_at", None)


# ============================================================
# CAREERS / JOB OPENINGS
# ============================================================

class JobOpeningSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"
    protocol = "https"


    def items(self):
        today = timezone.localdate()

        return (
            JobOpening.objects
            .filter(is_active=True)
            .filter(
                Q(last_date__isnull=True)
                | Q(last_date__gte=today)
            )
            .order_by("-created_at")
        )

    def location(self, obj):
        return reverse("job_detail", args=[obj.pk])

    def lastmod(self, obj):
        return (
            getattr(obj, "updated_at", None)
            or getattr(obj, "created_at", None)
        )
