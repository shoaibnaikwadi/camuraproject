import secrets
import string
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


from django.conf import settings
from django.db import models


def generate_referral_code():
    import secrets
    import string

    characters = string.ascii_uppercase + string.digits

    return "CAM" + "".join(
        secrets.choice(characters) for _ in range(8)
    )


class AffiliateProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="affiliate_profile",
    )

    referral_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_referral_code,
        db_index=True,
    )

    # Admin must approve the affiliate before links become active.
    is_enabled = models.BooleanField(default=False)
    application_submitted = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)

    # Only the affiliate's name and PhonePe mobile number.
    name = models.CharField(
        max_length=150,
        blank=True,
    )

    phonepe_mobile = models.CharField(
        max_length=10,
        blank=True,
    )

    invited_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invited_affiliates",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ({self.referral_code})"


class AffiliateCommissionRule(models.Model):
    """
    Fixed affiliate commission per unit sold for an individual
    product or a combo product.
    """

    product = models.OneToOneField(
        "home.Product",
        on_delete=models.PROTECT,
        related_name="affiliate_commission_rule",
    )

    commission_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=(
            "Fixed commission earned per unit sold. "
            "For a combo, this is the amount per combo kit."
        ),
    )

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product__name"]

    def __str__(self):
        return (
            f"{self.product.name}: "
            f"₹{self.commission_per_unit} per unit"
        )


class AffiliateOrderAttribution(models.Model):
    """
    Remembers which affiliate referred a particular order.
    """

    order = models.OneToOneField(
        "home.Order",
        on_delete=models.CASCADE,
        related_name="affiliate_attribution",
    )

    affiliate = models.ForeignKey(
        AffiliateProfile,
        on_delete=models.PROTECT,
        related_name="attributions",
    )

    referral_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Order #{self.order_id} "
            f"referred by {self.referral_code}"
        )


class AffiliateCommission(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"
        REJECTED = "rejected", "Rejected"
        REVERSED = "reversed", "Reversed"

    affiliate = models.ForeignKey(
        AffiliateProfile,
        on_delete=models.PROTECT,
        related_name="commissions",
    )

    order = models.ForeignKey(
        "home.Order",
        on_delete=models.PROTECT,
        related_name="affiliate_commissions",
    )

    # One commission record per OrderItem prevents duplicate rewards.
    order_item = models.OneToOneField(
        "home.OrderItem",
        on_delete=models.PROTECT,
        related_name="affiliate_commission",
    )

    rule = models.ForeignKey(
        AffiliateCommissionRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commissions",
    )

    # Snapshots preserve the commission calculation if the rule
    # or product name changes later.
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)

    quantity = models.PositiveIntegerField()
    commission_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.status == self.Status.PAID and not self.paid_at:
            self.paid_at = timezone.now()
        elif self.status != self.Status.PAID:
            self.paid_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.affiliate.referral_code}: "
            f"₹{self.commission_amount} "
            f"({self.get_status_display()})"
        )