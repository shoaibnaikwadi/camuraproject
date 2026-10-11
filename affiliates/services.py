from decimal import Decimal

from django.db import transaction
from home.models import OrderItem

from .models import (
    AffiliateProfile,
    AffiliateOrderAttribution,
    AffiliateCommissionRule,
    AffiliateCommission,
)


def attach_referral_to_order(request, order):
    """
    Save referral attribution when an order is created.

    Call this from every order-creation flow, including COD,
    Razorpay checkout and Buy Now.
    """

    referral_code = (
        request.session.get("affiliate_referral_code", "")
        .strip()
    )

    if not referral_code or not order.pk:
        return None

    affiliate = AffiliateProfile.objects.filter(
        referral_code__iexact=referral_code,
        is_enabled=True,
    ).first()

    if affiliate is None:
        return None

    # Never credit an affiliate for their own signed-in order.
    if order.user_id and affiliate.user_id == order.user_id:
        return None

    attribution, _ = AffiliateOrderAttribution.objects.get_or_create(
        order=order,
        defaults={
            "affiliate": affiliate,
            "referral_code": affiliate.referral_code,
        },
    )

    return attribution


@transaction.atomic
def create_affiliate_commissions_for_order(order):
    """
    Create commissions only when the order is delivered and paid.

    Each OrderItem is considered once. A combo receives its own
    configured commission; its individual components do not
    receive additional commissions from that same combo sale.
    """

    # Support either common order-status field name.
    status_values = [
        getattr(order, "status", ""),
        getattr(order, "order_status", ""),
    ]

    eligible_statuses = {"delivered", "completed"}

    is_delivered = any(
        str(value).strip().lower() in eligible_statuses
        for value in status_values
        if value
    )

    payment_status = str(
        getattr(order, "payment_status", "")
    ).strip().lower()

    is_paid = payment_status in {
        "paid",
        "captured",
        "completed",
        "successful",
        "success",
    }

    if not is_delivered or not is_paid:
        return 0

    attribution = (
        AffiliateOrderAttribution.objects
        .select_related("affiliate")
        .filter(order=order)
        .first()
    )

    if not attribution or not attribution.affiliate.is_enabled:
        return 0

    # Your existing code uses order.orderitem_set.
    order_items = list(
        OrderItem.objects
        .filter(order=order)
        .select_related("product")
    )

    product_ids = {
        item.product_id
        for item in order_items
        if item.product_id
    }

    rules = {
        rule.product_id: rule
        for rule in AffiliateCommissionRule.objects.filter(
            product_id__in=product_ids,
            is_active=True,
        )
    }

    created_count = 0

    for item in order_items:
        if not item.product_id or item.quantity < 1:
            continue

        rule = rules.get(item.product_id)

        # No rule means no commission for this product.
        if rule is None:
            continue

        commission_per_unit = rule.commission_per_unit
        amount = (
            commission_per_unit * item.quantity
        ).quantize(Decimal("0.01"))

        commission, created = AffiliateCommission.objects.get_or_create(
            order_item=item,
            defaults={
                "affiliate": attribution.affiliate,
                "order": order,
                "rule": rule,
                "product_name": (
                    getattr(item, "product_name", "")
                    or item.product.name
                ),
                "product_sku": (
                    getattr(item, "product_sku", "")
                    or item.product.sku
                ),
                "quantity": item.quantity,
                "commission_per_unit": commission_per_unit,
                "commission_amount": amount,
                "status": AffiliateCommission.Status.PENDING,
            },
        )

        if created:
            created_count += 1

    return created_count