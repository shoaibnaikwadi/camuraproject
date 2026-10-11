import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(
    post_save,
    sender="home.Order",
    dispatch_uid="affiliates_create_commissions_for_order",
)
def affiliate_order_saved(sender, instance, raw=False, **kwargs):
    if raw or not instance.pk:
        return

    order_id = instance.pk

    def create_commissions_safely():
        try:
            order = sender.objects.filter(pk=order_id).first()

            if order is None:
                return

            from .services import create_affiliate_commissions_for_order

            create_affiliate_commissions_for_order(order)

        except Exception:
            # Keep an order/payment save from failing because of
            # a commission-processing error. Check application logs.
            logger.exception(
                "Affiliate commission processing failed for order %s",
                order_id,
            )

    # Run after the order transaction commits.
    transaction.on_commit(create_commissions_safely)