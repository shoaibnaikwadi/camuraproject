from decimal import Decimal
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from home.models import Product

from .models import (
    AffiliateProfile,
    AffiliateOrderAttribution,
    AffiliateCommission,
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import AffiliateProfile


@login_required
def affiliate_apply(request):
    profile, _ = AffiliateProfile.objects.get_or_create(
        user=request.user
    )

    if profile.is_enabled:
        return redirect("affiliate:dashboard")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phonepe_mobile = request.POST.get(
            "phonepe_mobile", ""
        ).strip()

        if not name:
            messages.error(request, "Please enter your name.")

        elif (
            not phonepe_mobile.isascii()
            or not phonepe_mobile.isdigit()
            or len(phonepe_mobile) != 10
        ):
            messages.error(
                request,
                "Please enter a valid 10-digit PhonePe mobile number.",
            )

        else:
            profile.name = name
            profile.phonepe_mobile = phonepe_mobile
            profile.application_submitted = True
            profile.applied_at = timezone.now()
            profile.save()

            messages.success(
                request,
                "Your affiliate application has been submitted for review.",
            )

            return redirect("affiliate:dashboard")

    return render(
        request,
        "affiliates/apply.html",
        {"profile": profile},
    )


@login_required
def affiliate_dashboard(request):
    profile, _ = AffiliateProfile.objects.get_or_create(
        user=request.user
    )

    # Commission records are separate from referred orders.
    commissions = (
        AffiliateCommission.objects
        .filter(affiliate=profile)
        .select_related("order", "order_item")
        .order_by("-created_at")
    )

    # Fetch orders attributed to this affiliate.
    attributions = (
        AffiliateOrderAttribution.objects
        .filter(affiliate=profile)
        .select_related("order")
        .order_by("-created_at")
    )

    total_pending = (
        commissions.filter(status="pending")
        .aggregate(total=Sum("commission_amount"))["total"]
        or Decimal("0.00")
    )

    total_approved = (
        commissions.filter(status="approved")
        .aggregate(total=Sum("commission_amount"))["total"]
        or Decimal("0.00")
    )

    total_paid = (
        commissions.filter(status="paid")
        .aggregate(total=Sum("commission_amount"))["total"]
        or Decimal("0.00")
    )

    product_links = []
    referral_url = ""

    if profile.is_enabled:
        referral_query = urlencode({
            "ref": profile.referral_code
        })

        listing_url = request.build_absolute_uri(
            reverse("product_list")
        )
        referral_url = f"{listing_url}?{referral_query}"

        products = Product.objects.filter(
            is_active=True
        ).order_by("product_type", "name")

        for product in products:
            detail_url = request.build_absolute_uri(
                reverse("product_detail", args=[product.pk])
            )

            product_links.append({
                "name": product.name,
                "sku": product.sku,
                "product_type": product.get_product_type_display(),
                "url": f"{detail_url}?{referral_query}",
            })

    return render(
        request,
        "affiliates/dashboard.html",
        {
            "profile": profile,
            "commissions": commissions,
            "attributions": attributions,
            "total_pending": total_pending,
            "total_approved": total_approved,
            "total_paid": total_paid,
            "referral_url": referral_url,
            "product_links": product_links,
        },
    )