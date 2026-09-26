from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import (
    ComboProduct,
    Camera,
    CameraBullet,
    DVR,
    HardDisk,
    Cable,
    PowerSupply,
    Accessory,
)


# ============================================================
# STATIC PAGES
# ============================================================

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
            "privacy_policy",
            "terms_and_conditions",
            "refund_cancellation_policy",
            "accessories",
        ]

    def location(self, item):
        return reverse(item)


# ============================================================
# COMBO PRODUCTS
# ============================================================

class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return ComboProduct.objects.all()

    def location(self, obj):
        return reverse("product_detail", args=[obj.pk])

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, "updated_at") else None


# ============================================================
# CAMERA PRODUCTS
# ============================================================

class CameraSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return Camera.objects.all()

    def location(self, obj):
        return reverse("camera_detail", args=[obj.pk])


# ============================================================
# BULLET CAMERA PRODUCTS
# ============================================================

class BulletCameraSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return CameraBullet.objects.all()

    def location(self, obj):
        return reverse("bullet_camera_detail", args=[obj.pk])


# ============================================================
# DVR PRODUCTS
# ============================================================

class DVRSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return DVR.objects.all()

    def location(self, obj):
        return reverse("dvr_detail", args=[obj.pk])


# ============================================================
# HARD DISK PRODUCTS
# ============================================================

class HardDiskSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return HardDisk.objects.all()

    def location(self, obj):
        return reverse("hard_disk_detail", args=[obj.pk])


# ============================================================
# CABLE PRODUCTS
# ============================================================

class CableSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return Cable.objects.all()

    def location(self, obj):
        return reverse("cable_detail", args=[obj.pk])


# ============================================================
# POWER SUPPLY PRODUCTS
# ============================================================

class PowerSupplySitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return PowerSupply.objects.all()

    def location(self, obj):
        return reverse("power_supply_detail", args=[obj.pk])


# ============================================================
# ACCESSORIES
# ============================================================

# class AccessorySitemap(Sitemap):
#     priority = 0.8
#     changefreq = "daily"

#     def items(self):
#         return Accessory.objects.all()

#     def location(self, obj):
#         return reverse("accessory_detail", args=[obj.pk])