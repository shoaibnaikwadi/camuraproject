from django.contrib import admin
from django.utils import timezone

from .models import (
    AffiliateProfile,
    AffiliateCommissionRule,
    AffiliateOrderAttribution,
    AffiliateCommission,
)


@admin.register(AffiliateProfile)
class AffiliateProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "referral_code",
        "application_submitted",
        "is_enabled",
        "applied_at",
        "created_at",
    )

    list_filter = ("is_enabled", "application_submitted")
    search_fields = (
        "user__username",
        "user__email",
        "referral_code",
    )

    list_editable = ("is_enabled",)

    readonly_fields = ("referral_code", "created_at")


@admin.register(AffiliateCommissionRule)
class AffiliateCommissionRuleAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "commission_per_unit",
        "is_active",
        "updated_at",
    )

    list_filter = ("is_active",)
    search_fields = ("product__name", "product__sku")
    autocomplete_fields = ("product",)


@admin.register(AffiliateOrderAttribution)
class AffiliateOrderAttributionAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "affiliate",
        "referral_code",
        "created_at",
    )

    search_fields = (
        "referral_code",
        "affiliate__referral_code",
        "affiliate__user__username",
    )

    readonly_fields = (
        "order",
        "affiliate",
        "referral_code",
        "created_at",
    )

@admin.register(AffiliateCommission)
class AffiliateCommissionAdmin(admin.ModelAdmin):

    list_display = (
        "affiliate",
        "order",
        "product_name",
        "quantity",
        "commission_per_unit",
        "commission_amount",
        "status",
        "created_at",
        "paid_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "affiliate__user__username",
        "affiliate__referral_code",
        "product_name",
        "product_sku",
    )

    # Only status can be edited on an existing commission.
    readonly_fields = (
        "affiliate",
        "order",
        "order_item",
        "rule",
        "product_name",
        "product_sku",
        "quantity",
        "commission_per_unit",
        "commission_amount",
        "created_at",
        "paid_at",
    )

    actions = (
        "approve_selected",
        "mark_selected_paid",
        "reject_selected",
    )

    # Commission records must be created by the commission service.
    def has_add_permission(self, request):
        return False

    # Preserve the commission audit history.
    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Approve selected pending commissions")
    def approve_selected(self, request, queryset):
        updated = queryset.filter(
            status=AffiliateCommission.Status.PENDING
        ).update(
            status=AffiliateCommission.Status.APPROVED
        )

        self.message_user(
            request,
            f"{updated} commission(s) approved.",
        )

    @admin.action(description="Mark selected approved commissions as paid")
    def mark_selected_paid(self, request, queryset):
        updated = 0

        for commission in queryset.filter(
            status=AffiliateCommission.Status.APPROVED
        ):
            commission.status = AffiliateCommission.Status.PAID
            commission.save(update_fields=["status", "paid_at"])
            updated += 1

        self.message_user(
            request,
            f"{updated} commission(s) marked as paid.",
        )

    @admin.action(description="Reject selected pending commissions")
    def reject_selected(self, request, queryset):
        updated = queryset.filter(
            status=AffiliateCommission.Status.PENDING
        ).update(
            status=AffiliateCommission.Status.REJECTED
        )

        self.message_user(
            request,
            f"{updated} commission(s) rejected.",
        )