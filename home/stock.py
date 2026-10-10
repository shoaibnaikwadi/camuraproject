from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Order, OrderItem, Product, ComboComponent


@transaction.atomic
def deduct_order_stock(order):
    """
    Deduct stock for an order exactly once.

    Single product:
        Deduct its own stock.

    Combo product:
        Deduct the stock of each included component.
    """

    # Lock the order to prevent duplicate stock deductions.
    locked_order = (
        Order.objects
        .select_for_update()
        .get(pk=order.pk)
    )

    if locked_order.stock_deducted:
        return locked_order

    order_items = list(
        OrderItem.objects
        .filter(order=locked_order)
        .select_related("product")
    )

    if not order_items:
        raise ValidationError(
            "Cannot deduct stock because this order has no items."
        )

    # Total quantity needed for each physical product.
    required_stock = defaultdict(int)

    for item in order_items:
        product = item.product

        if not product:
            raise ValidationError(
                "An order item is missing its product."
            )

        if item.quantity < 1:
            raise ValidationError(
                f"Invalid quantity for {product.name}."
            )

        # Individual product.
        if product.product_type == Product.ProductType.SINGLE:
            required_stock[product.pk] += item.quantity

        # Combo kit: deduct its individual components.
        elif product.product_type == Product.ProductType.COMBO:
            components = list(
                ComboComponent.objects
                .filter(combo_id=product.pk)
                .values_list("component_id", "quantity")
            )

            if not components:
                raise ValidationError(
                    f"The combo '{product.name}' has no components."
                )

            for component_id, component_quantity in components:
                required_stock[component_id] += (
                    component_quantity * item.quantity
                )

        else:
            raise ValidationError(
                f"Unknown product type for '{product.name}'."
            )

    # Lock all affected inventory rows in a consistent order.
    products = list(
        Product.objects
        .select_for_update()
        .filter(pk__in=required_stock.keys())
        .order_by("pk")
    )

    products_by_id = {
        product.pk: product for product in products
    }

    # Check every required quantity before changing any stock.
    for product_id, required_quantity in required_stock.items():
        product = products_by_id.get(product_id)

        if product is None:
            raise ValidationError(
                "A product required by this order no longer exists."
            )

        if product.stock < required_quantity:
            raise ValidationError(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.stock}; "
                f"required: {required_quantity}."
            )

    # Deduct all stock only after every item passes validation.
    for product_id, required_quantity in required_stock.items():
        product = products_by_id[product_id]
        product.stock -= required_quantity
        product.save(update_fields=["stock", "updated_at"])

    # Mark the order so the operation cannot run twice.
    locked_order.stock_deducted = True
    locked_order.save(update_fields=["stock_deducted"])

    return locked_order