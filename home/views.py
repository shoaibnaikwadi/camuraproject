
# ============================================================
# IMPORTS
# ============================================================

import csv
import random
from decimal import Decimal, ROUND_HALF_UP

import razorpay
import requests

from decouple import config

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# ============================================================
# MODELS
# ============================================================

from .models import (
    Order,
    OrderItem,
    CartItem,
    ComboProduct,
    CustomerProfile,
    Profile,
    Camera,
    CameraBullet,
    DVR,
    HardDisk,
    Cable,
    PowerSupply,
    Accessory,
    InstallationCharge,
    ServiceBooking,
)


# ============================================================
# FORMS
# ============================================================

from .forms import (
    CustomerProfileForm,
    ServiceBookingForm,
    CameraForm,
    CableForm,
    PowerSupplyForm,
    AccessoryForm,
    InstallationForm,
    ComboForm,
    CCTVEngineerForm,
)


# ============================================================
# CONSTANTS
# ============================================================

MINIMUM_ORDER = Decimal("5000.00")

PRODUCT_MODELS = {
    "combo": ComboProduct,
    "camera": Camera,
    "bullet_camera": CameraBullet,
    "dvr": DVR,
    "hard_disk": HardDisk,
    "cable": Cable,
    "power_supply": PowerSupply,
    "accessory": Accessory,
}


# ============================================================
# HOME
# ============================================================

def home(request):
    return render(request, "home/index.html")


# ============================================================
# AUTHENTICATION / REGISTRATION
# ============================================================

def registerold(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                f"Account created for {user.username}! "
                "You can now log in."
            )

            return redirect("login")

    else:
        form = UserCreationForm()

    return render(
        request,
        "home/registerold.html",
        {"form": form},
    )


# ============================================================
# PRODUCT LIST
# ============================================================

def product_list(request):

    if request.user.is_authenticated:

        try:
            profile = request.user.profile

            if not profile.full_name or not profile.email:
                return redirect("profile")

        except Profile.DoesNotExist:

            Profile.objects.create(
                user=request.user
            )

            return redirect("profile")

    combos = ComboProduct.objects.all()

    return render(
        request,
        "home/product_list.html",
        {"combos": combos},
    )


# ============================================================
# PRODUCT DETAIL
# ============================================================

def product_detail(request, pk):

    combo = get_object_or_404(
        ComboProduct,
        pk=pk,
    )

    discount = None

    price = combo.total_price()

    if combo.mrp and combo.mrp > price:

        discount = round(
            (combo.mrp - price)
            / combo.mrp
            * 100
        )

    return render(
        request,
        "home/product_detail.html",
        {
            "combo": combo,
            "discount": discount,
        },
    )


# ============================================================
# ACCESSORIES
# ============================================================

def get_accessory_products():

    products = []

    categories = [

        (
            Camera,
            "Camera",
            "camera_type",
            "camera",
        ),

        (
            CameraBullet,
            "Bullet Camera",
            "bullet_camera_type",
            "bullet_camera",
        ),

        (
            DVR,
            "DVR",
            "dvr_name",
            "dvr",
        ),

        (
            HardDisk,
            "Hard Disk",
            "size",
            "hard_disk",
        ),

        (
            Cable,
            "Cable",
            "length",
            "cable",
        ),

        (
            PowerSupply,
            "Power Supply",
            "range_slug",
            "power_supply",
        ),

        (
            Accessory,
            "Accessory",
            "name",
            "accessory",
        ),
    ]

    for model, category, name_field, product_type in categories:

        for item in model.objects.all():

            name = getattr(
                item,
                name_field,
                ""
            )

            model_number = (
                getattr(
                    item,
                    "model_number",
                    None,
                )
                or
                getattr(
                    item,
                    "bullet_model_number",
                    None,
                )
                or ""
            )

            products.append(
                {
                    "id": item.pk,
                    "name": name,
                    "category": category,
                    "product_type": product_type,
                    "model_number": model_number,
                    "price": item.price,
                    "stock": item.stock,
                    "image": item.image,
                }
            )

    return products


def accessories(request):

    query = request.GET.get(
        "q",
        "",
    ).strip()

    category = request.GET.get(
        "category",
        "",
    ).strip()

    products = get_accessory_products()

    if category:

        products = [
            product
            for product in products
            if product["category"] == category
        ]

    if query:

        query_lower = query.lower()

        products = [
            product
            for product in products
            if query_lower in (
                product["name"]
                + " "
                + (product["model_number"] or "")
            ).lower()
        ]

    products.sort(
        key=lambda product: product["name"].lower()
    )

    return render(
        request,
        "home/accessories.html",
        {
            "products": products,
            "query": query,
            "selected_category": category,
            "categories": [
                "Camera",
                "Bullet Camera",
                "DVR",
                "Hard Disk",
                "Cable",
                "Power Supply",
                "Accessory",
            ],
        },
    )


def accessory_suggestions(request):

    query = request.GET.get(
        "q",
        "",
    ).strip()

    if len(query) < 2:

        return JsonResponse(
            {"suggestions": []}
        )

    products = get_accessory_products()

    query_lower = query.lower()

    matches = [

        {
            "name": product["name"],
            "category": product["category"],
            "model_number": product["model_number"],
        }

        for product in products

        if query_lower in (
            product["name"]
            + " "
            + (product["model_number"] or "")
        ).lower()
    ]

    return JsonResponse(
        {
            "suggestions": matches[:8]
        }
    )


# ============================================================
# CART
# ============================================================

@login_required
@require_POST
def add_to_cart(
    request,
    product_type,
    product_id,
):

    model = PRODUCT_MODELS.get(
        product_type
    )

    if model is None:

        messages.error(
            request,
            "Invalid product."
        )

        return redirect("product_list")

    product = get_object_or_404(
        model,
        pk=product_id,
    )

    try:

        qty = int(
            request.POST.get(
                "qty",
                request.POST.get(
                    "quantity",
                    1,
                ),
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        messages.error(
            request,
            "Invalid quantity."
        )

        return redirect("cart")

    if qty < 1:

        messages.error(
            request,
            "Quantity must be at least 1."
        )

        return redirect("cart")

    with transaction.atomic():

        User.objects.select_for_update().get(
            pk=request.user.pk
        )

        cart_item, created = (
            CartItem.objects.get_or_create(
                user=request.user,
                **{
                    product_type: product
                },
                defaults={
                    "quantity": qty
                },
            )
        )

        if not created:

            cart_item.quantity += qty

        try:

            cart_item.full_clean()

        except ValidationError as exc:

            messages.error(
                request,
                "; ".join(
                    exc.messages
                ),
            )

            if created:
                cart_item.delete()

            return redirect("cart")

        cart_item.save()

    messages.success(
        request,
        f"{cart_item.product_name} added to cart."
    )

    return redirect("cart")


@login_required
def cart(request):

    items = (
        CartItem.objects
        .filter(user=request.user)
        .select_related(
            "combo",
            "camera",
            "bullet_camera",
            "dvr",
            "hard_disk",
            "cable",
            "power_supply",
            "accessory",
        )
    )

    total = sum(
        (
            item.subtotal()
            for item in items
        ),
        Decimal("0.00"),
    )

    return render(
        request,
        "home/cart.html",
        {
            "items": items,
            "total": total,
        },
    )


@login_required
@require_POST
def remove_cart_item(
    request,
    item_id,
):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user,
    )

    cart_item.delete()

    messages.success(
        request,
        "Product removed from your cart."
    )

    return redirect("cart")


@login_required
@require_POST
def clear_cart(request):

    CartItem.objects.filter(
        user=request.user
    ).delete()

    messages.success(
        request,
        "Your cart has been cleared."
    )

    return redirect("cart")


# ============================================================
# SELECT ADDRESS
# ============================================================

@login_required
def select_address(request):

    from_page = (
        request.GET.get("from")
        or request.POST.get("from")
        or ""
    )

    combo_id = (
        request.GET.get("combo_id")
        or request.POST.get("combo_id")
        or ""
    )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        # Existing address
        address_id = request.POST.get(
            "address_id"
        )

        if address_id:

            address = get_object_or_404(
                CustomerProfile,
                id=address_id,
                user=request.user,
            )

            request.session[
                "selected_address_id"
            ] = address.id

            if from_page == "buy_now" and combo_id:

                request.session[
                    "buy_now_combo_id"
                ] = combo_id

                return redirect(
                    "process_buy_now",
                    combo_id=combo_id,
                )

            return redirect(
                "checkout_page"
            )

        # ----------------------------------------------------
        # New address
        # ----------------------------------------------------

        required_fields = [
            "full_name",
            "email",
            "mobile",
            "pincode",
            "address",
            "city",
            "state",
        ]

        values = {
            field: request.POST.get(field)
            for field in required_fields
        }

        if not all(values.values()):

            messages.error(
                request,
                "Please fill all address fields."
            )

        else:

            new_address = (
                CustomerProfile.objects.create(
                    user=request.user,
                    **values,
                )
            )

            request.session[
                "selected_address_id"
            ] = new_address.id

            messages.success(
                request,
                "Address added successfully."
            )

            return redirect(
                f"{request.path}"
                f"?from={from_page}"
                f"&combo_id={combo_id}"
            )

    # --------------------------------------------------------
    # ADDRESSES
    # --------------------------------------------------------

    addresses = (
        CustomerProfile.objects
        .filter(user=request.user)
        .order_by("-id")
    )

    selected_address_id = request.session.get(
        "selected_address_id"
    )

    if addresses.exists():

        if not addresses.filter(
            id=selected_address_id
        ).exists():

            selected_address_id = (
                addresses.first().id
            )

            request.session[
                "selected_address_id"
            ] = selected_address_id

    else:

        selected_address_id = None

        request.session.pop(
            "selected_address_id",
            None,
        )

    # --------------------------------------------------------
    # CART SUMMARY
    # --------------------------------------------------------

    items = []
    total = Decimal("0.00")

    if from_page != "buy_now":

        cart_items = (
            CartItem.objects
            .filter(user=request.user)
            .select_related(
                "combo",
                "camera",
                "bullet_camera",
                "dvr",
                "hard_disk",
                "cable",
                "power_supply",
                "accessory",
            )
        )

        for item in cart_items:

            subtotal = item.subtotal()

            items.append(
                {
                    "name": item.product_name,
                    "qty": item.quantity,
                    "price": item.unit_price,
                    "subtotal": subtotal,
                }
            )

            total += subtotal

    elif combo_id:

        combo = get_object_or_404(
            ComboProduct,
            pk=combo_id,
        )

        total = combo.total_price()

        items = [
            {
                "name": combo.name,
                "qty": 1,
                "price": total,
                "subtotal": total,
            }
        ]

    return render(
        request,
        "home/select_address.html",
        {
            "addresses": addresses,
            "selected_address_id": selected_address_id,
            "from_page": from_page,
            "combo_id": combo_id,
            "items": items,
            "total": total,
        },
    )


@login_required
@require_POST
def delete_address(
    request,
    id,
):

    address = get_object_or_404(
        CustomerProfile,
        id=id,
        user=request.user,
    )

    selected_address_id = request.session.get(
        "selected_address_id"
    )

    address.delete()

    if selected_address_id == id:

        next_address = (
            CustomerProfile.objects
            .filter(user=request.user)
            .order_by("-id")
            .first()
        )

        if next_address:

            request.session[
                "selected_address_id"
            ] = next_address.id

        else:

            request.session.pop(
                "selected_address_id",
                None,
            )

    messages.success(
        request,
        "Address deleted successfully."
    )

    return redirect(
        "select_address"
    )


# ============================================================
# CHECKOUT
# ============================================================

@login_required
@require_POST
def cart_checkout(request):

    address_id = request.session.get(
        "selected_address_id"
    )

    if not address_id:

        messages.error(
            request,
            "Please select a delivery address."
        )

        return redirect(
            "select_address"
        )

    profile = get_object_or_404(
        CustomerProfile,
        id=address_id,
        user=request.user,
    )

    cart_items = list(
        CartItem.objects
        .filter(user=request.user)
        .select_related(
            "combo",
            "camera",
            "bullet_camera",
            "dvr",
            "hard_disk",
            "cable",
            "power_supply",
            "accessory",
        )
    )

    if not cart_items:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    # Validate cart
    for item in cart_items:

        try:
            item.full_clean()

        except ValidationError as exc:

            messages.error(
                request,
                f"{item.product_name}: "
                f"{'; '.join(exc.messages)}"
            )

            return redirect("cart")

    total = sum(
        (
            item.subtotal()
            for item in cart_items
        ),
        Decimal("0.00"),
    )

    if total <= MINIMUM_ORDER:

        messages.error(
            request,
            "Minimum order value must be more than ₹5,000."
        )

        return redirect("cart")

    # --------------------------------------------------------
    # CREATE LOCAL ORDER
    # --------------------------------------------------------

    with transaction.atomic():

        order = Order.objects.create(
            user=request.user,
            profile=profile,
            total_amount=total,
            payment_method="online",
            payment_status="Pending",
        )

        for item in cart_items:

            product_fields = {
                field: getattr(
                    item,
                    field,
                )
                for field in CartItem.PRODUCT_FIELDS
            }

            OrderItem.objects.create(
                order=order,
                **product_fields,
                product_name=item.product_name,
                quantity=item.quantity,
                price=item.unit_price,
            )

    # --------------------------------------------------------
    # CREATE RAZORPAY ORDER
    # --------------------------------------------------------

    amount_paise = int(
        (
            total * 100
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    try:

        payment = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1,
            }
        )

    except Exception as exc:

        print(
            "Razorpay order creation error:",
            exc,
        )

        order.delete()

        messages.error(
            request,
            "Unable to initiate online payment. "
            "Please try again."
        )

        return redirect("cart")

    order.razorpay_order_id = payment["id"]

    order.save(
        update_fields=[
            "razorpay_order_id"
        ]
    )

    return render(
        request,
        "home/payment.html",
        {
            "order": order,
            "profile": profile,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": total,
            "amount_paise": amount_paise,
            "payment_id": payment["id"],
        },
    )


# ============================================================
# BUY NOW
# ============================================================

@login_required
def buy_now(
    request,
    combo_id,
):

    combo = get_object_or_404(
        ComboProduct,
        pk=combo_id,
    )

    request.session[
        "buy_now_combo_id"
    ] = combo.id

    return redirect(
        f"{reverse('select_address')}"
        f"?from=buy_now"
        f"&combo_id={combo.id}"
    )


@login_required
def process_buy_now(
    request,
    combo_id,
):

    address_id = request.session.get(
        "selected_address_id"
    )

    if not address_id:

        return redirect(
            f"{reverse('select_address')}"
            f"?from=buy_now"
            f"&combo_id={combo_id}"
        )

    profile = get_object_or_404(
        CustomerProfile,
        id=address_id,
        user=request.user,
    )

    combo = get_object_or_404(
        ComboProduct,
        pk=combo_id,
    )

    total = combo.total_price()

    if total <= 0:

        messages.error(
            request,
            "Invalid product price."
        )

        return redirect(
            "product_detail",
            pk=combo.id,
        )

    amount_paise = int(
        (
            total * 100
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    try:

        payment = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1,
            }
        )

    except Exception as exc:

        print(
            "Razorpay Buy Now error:",
            exc,
        )

        messages.error(
            request,
            "Unable to initiate payment. "
            "Please try again."
        )

        return redirect(
            "product_detail",
            pk=combo.id,
        )

    order = Order.objects.create(
        user=request.user,
        profile=profile,
        total_amount=total,
        payment_method="online",
        payment_status="Pending",
        razorpay_order_id=payment["id"],
    )

    OrderItem.objects.create(
        order=order,
        combo=combo,
        quantity=1,
        price=combo.total_price(),
    )

    return render(
        request,
        "home/payment.html",
        {
            "order": order,
            "profile": profile,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": total,
            "amount_paise": amount_paise,
            "payment_id": payment["id"],
        },
    )


# ============================================================
# ONLINE PRODUCT PAYMENT SUCCESS
# ============================================================

@csrf_exempt
@require_POST
def payment_success(request):

    razorpay_order_id = request.POST.get(
        "razorpay_order_id"
    )

    razorpay_payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    razorpay_signature = request.POST.get(
        "razorpay_signature"
    )

    if not all(
        [
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature,
        ]
    ):

        return render(
            request,
            "home/payment_failed.html",
            {
                "error":
                    "Missing payment details."
            },
        )

    order = get_object_or_404(
        Order,
        razorpay_order_id=razorpay_order_id,
        payment_method="online",
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    try:

        client.utility.verify_payment_signature(
            params_dict
        )

    except razorpay.errors.SignatureVerificationError:

        order.payment_status = "Failed"

        order.save(
            update_fields=[
                "payment_status"
            ]
        )

        return render(
            request,
            "home/payment_failed.html",
            {
                "error":
                    "Payment signature verification failed."
            },
        )

    # Already processed
    if order.payment_status == "Paid":

        return redirect(
            "order_success",
            order_id=order.id,
        )

    # --------------------------------------------------------
    # PAYMENT VERIFIED
    # --------------------------------------------------------

    order.payment_id = razorpay_payment_id
    order.payment_status = "Paid"

    order.save(
        update_fields=[
            "payment_id",
            "payment_status",
        ]
    )

    # Clear cart only after verified payment
    CartItem.objects.filter(
        user=order.user
    ).delete()

    # Clear checkout session
    request.session.pop(
        "selected_address_id",
        None,
    )

    request.session.pop(
        "buy_now_combo_id",
        None,
    )

    messages.success(
        request,
        "Payment successful! "
        "Your order has been placed."
    )

    return redirect(
        "order_success",
        order_id=order.id,
    )


# ============================================================
# COD PAYMENT
# ============================================================

@login_required
@require_POST
def cod_payment(request):

    order_id = request.POST.get(
        "order_id"
    )

    if not order_id:

        messages.error(
            request,
            "Invalid order."
        )

        return redirect("cart")

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    if order.payment_status != "Pending":

        messages.error(
            request,
            "This order has already been processed."
        )

        return redirect(
            "order_success",
            order_id=order.id,
        )

    order.payment_method = "cod"
    order.payment_status = "Pending"
    order.razorpay_order_id = None

    order.save(
        update_fields=[
            "payment_method",
            "payment_status",
            "razorpay_order_id",
        ]
    )

    CartItem.objects.filter(
        user=request.user
    ).delete()

    request.session.pop(
        "selected_address_id",
        None,
    )

    request.session.pop(
        "buy_now_combo_id",
        None,
    )

    messages.success(
        request,
        f"Order #{order.id} placed successfully!"
    )

    return redirect(
        "order_success",
        order_id=order.id,
    )


# ============================================================
# ORDER SUCCESS
# ============================================================

@login_required
def order_success(
    request,
    order_id,
):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "home/order_success.html",
        {
            "order": order,
        },
    )


# ============================================================
# MY ORDERS
# ============================================================

@login_required
def my_orders(request):

    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "home/my_orders.html",
        {
            "orders": orders,
        },
    )


# ============================================================
# PROFILE
# ============================================================

@login_required
def profile(request):

    profile = request.user.profile

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name"
        )

        email = request.POST.get(
            "email"
        )

        if not full_name:

            messages.error(
                request,
                "Full name is required."
            )

            return redirect("profile")

        profile.full_name = full_name
        profile.email = email
        profile.save()

        messages.success(
            request,
            "Profile updated successfully!"
        )

        return redirect(
            "product_list"
        )

    return render(
        request,
        "home/profile.html",
        {
            "profile": profile
        },
    )


# ============================================================
# CUSTOMER ADDRESS LIST
# ============================================================

@login_required
def address_list(request):

    addresses = (
        CustomerProfile.objects
        .filter(user=request.user)
        .order_by("-id")
    )

    # ADD
    if (
        request.method == "POST"
        and request.POST.get("form_type") == "add"
    ):

        CustomerProfile.objects.create(
            user=request.user,
            full_name=request.POST.get(
                "full_name"
            ),
            email=request.POST.get(
                "email"
            ),
            mobile=request.POST.get(
                "mobile"
            ),
            pincode=request.POST.get(
                "pincode"
            ),
            address=request.POST.get(
                "address"
            ),
            city=request.POST.get(
                "city"
            ),
            state=request.POST.get(
                "state"
            ),
        )

        messages.success(
            request,
            "Address added successfully!"
        )

        return redirect(
            "address_list"
        )

    # EDIT
    if (
        request.method == "POST"
        and request.POST.get("form_type") == "edit"
    ):

        address = get_object_or_404(
            CustomerProfile,
            id=request.POST.get(
                "address_id"
            ),
            user=request.user,
        )

        address.full_name = request.POST.get(
            "full_name"
        )

        address.email = request.POST.get(
            "email"
        )

        address.mobile = request.POST.get(
            "mobile"
        )

        address.pincode = request.POST.get(
            "pincode"
        )

        address.address = request.POST.get(
            "address"
        )

        address.city = request.POST.get(
            "city"
        )

        address.state = request.POST.get(
            "state"
        )

        address.save()

        messages.success(
            request,
            "Address updated successfully!"
        )

        return redirect(
            "address_list"
        )

    return render(
        request,
        "home/addresses.html",
        {
            "addresses": addresses
        },
    )


@login_required
@require_POST
def delete_address_from_list(
    request,
    id,
):

    address = get_object_or_404(
        CustomerProfile,
        id=id,
        user=request.user,
    )

    address.delete()

    messages.success(
        request,
        "Address deleted."
    )

    return redirect(
        "address_list"
    )


# ============================================================
# CONTACT
# ============================================================

def contact_view(request):

    if request.method == "POST":

        name = request.POST.get(
            "name"
        )

        email = request.POST.get(
            "email"
        )

        message = request.POST.get(
            "message"
        )

        send_mail(
            subject=f"New Contact Message from {name}",
            message=(
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[
                settings.DEFAULT_FROM_EMAIL
            ],
            fail_silently=True,
        )

        messages.success(
            request,
            "Thank you for contacting us! "
            "We'll get back to you soon."
        )

        return redirect(
            "contact"
        )

    return render(
        request,
        "home/contact.html"
    )


# ============================================================
# INFORMATION PAGES
# ============================================================

def privacy_policy(request):
    return render(
        request,
        "home/privacy_policy.html"
    )


def shipping_policy(request):
    return render(
        request,
        "home/shipping_policy.html"
    )


def warranty(request):
    return render(
        request,
        "home/warranty.html"
    )


def terms_and_conditions(request):
    return render(
        request,
        "home/terms_and_conditions.html"
    )


def refund_cancellation_policy(request):
    return render(
        request,
        "home/refund_cancellation_policy.html"
    )


# ============================================================
# GOOGLE PRODUCT FEED
# ============================================================

def google_feed(request):

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    response["Content-Disposition"] = (
        'inline; filename="google_feed.csv"'
    )

    writer = csv.writer(response)

    writer.writerow(
        [
            "id",
            "title",
            "description",
            "link",
            "image_link",
            "price",
            "availability",
            "condition",
            "brand",
            "google_product_category",
            "mpn",
            "product_type",
            "included_items",
            "identifier_exists",
        ]
    )

    # --------------------------------------------------------
    # COMBO PRODUCTS
    # --------------------------------------------------------

    for combo in ComboProduct.objects.all():

        if combo.available_stock <= 0:
            continue

        components = [
            f"Camera: {combo.camera} x {combo.camera_qty}",
            f"DVR: {combo.dvr}",
        ]

        if combo.cameraBullet:

            components.append(
                f"Bullet Camera: "
                f"{combo.cameraBullet} x "
                f"{combo.camerabullet_qty}"
            )

        if combo.hard_disk:

            components.append(
                f"Hard Disk: "
                f"{combo.hard_disk} x "
                f"{combo.hard_disk_qty}"
            )

        components.extend(
            [
                f"Cable: {combo.cable} x {combo.cable_qty}",
                f"Power Supply: {combo.power} x {combo.power_qty}",
                f"BNC Connector: {combo.bnc_connector} x {combo.bnc_qty}",
                f"DC Connector: {combo.dc_connector} x {combo.dc_qty}",
                f"Installation: {combo.installation} x {combo.installation_qty}",
            ]
        )

        included_items = ", ".join(
            components
        )

        desc = strip_tags(
            combo.description or ""
        )

        desc = (
            f"{desc}\n\n"
            f"Included in Combo:\n"
            f"{included_items}"
        )

        link = request.build_absolute_uri(
            f"/product/{combo.id}/"
        )

        if combo.image:

            image = request.build_absolute_uri(
                combo.image.url
            )

        else:

            image = request.build_absolute_uri(
                "/static/no-image.jpg"
            )

        writer.writerow(
            [
                f"combo-{combo.id}",
                combo.name,
                desc[:5000],
                link,
                image,
                f"{combo.total_price():.2f} INR",
                "in_stock",
                "new",
                combo.brand or "Generic",
                "6720",
                f"SV-COMBO-{combo.id}",
                "CCTV Combo Kit",
                included_items,
                "FALSE",
            ]
        )

    # --------------------------------------------------------
    # INDIVIDUAL PRODUCTS
    # --------------------------------------------------------

    def write_product(
        product,
        product_id,
        title,
        description,
        product_type,
        mpn,
        category="6720",
    ):

        if product.stock <= 0:
            return

        if product.image:

            image = request.build_absolute_uri(
                product.image.url
            )

        else:

            image = request.build_absolute_uri(
                "/static/no-image.jpg"
            )

        link = request.build_absolute_uri(
            "/accessories/"
        )

        writer.writerow(
            [
                product_id,
                title,
                description[:5000],
                link,
                image,
                f"{product.price:.2f} INR",
                "in_stock",
                "new",
                "Generic",
                category,
                mpn,
                product_type,
                "",
                "FALSE",
            ]
        )

    # Cameras
    for product in Camera.objects.all():

        title = product.camera_type

        if product.model_number:
            title += f" - {product.model_number}"

        write_product(
            product,
            f"camera-{product.id}",
            title,
            f"{title}. CCTV security camera from Camura.in.",
            "CCTV Camera",
            product.model_number
            or f"SV-CAMERA-{product.id}",
        )

    # Bullet Cameras
    for product in CameraBullet.objects.all():

        title = product.bullet_camera_type

        if product.bullet_model_number:
            title += f" - {product.bullet_model_number}"

        write_product(
            product,
            f"bullet-camera-{product.id}",
            title,
            f"{title}. CCTV bullet camera from Camura.in.",
            "CCTV Bullet Camera",
            product.bullet_model_number
            or f"SV-BULLET-{product.id}",
        )

    # DVR
    for product in DVR.objects.all():

        title = product.dvr_name

        if product.model_number:
            title += f" - {product.model_number}"

        write_product(
            product,
            f"dvr-{product.id}",
            title,
            f"{title}. CCTV DVR from Camura.in.",
            "CCTV DVR",
            product.model_number
            or f"SV-DVR-{product.id}",
        )

    # Hard Disk
    for product in HardDisk.objects.all():

        title = (
            f"CCTV Hard Disk "
            f"{product.size}"
        )

        write_product(
            product,
            f"hard-disk-{product.id}",
            title,
            (
                f"{title} for CCTV surveillance "
                f"recording from Camura.in."
            ),
            "CCTV Hard Disk",
            f"SV-HDD-{product.id}",
        )

    # Cable
    for product in Cable.objects.all():

        title = (
            f"CCTV Cable "
            f"{product.length}"
        )

        write_product(
            product,
            f"cable-{product.id}",
            title,
            (
                f"{title} for CCTV installation "
                f"from Camura.in."
            ),
            "CCTV Cable",
            f"SV-CABLE-{product.id}",
        )

    # Power Supply
    for product in PowerSupply.objects.all():

        title = (
            f"CCTV Power Supply "
            f"{product.range_slug}"
        )

        write_product(
            product,
            f"power-supply-{product.id}",
            title,
            (
                f"{title} for CCTV installation "
                f"from Camura.in."
            ),
            "CCTV Power Supply",
            f"SV-PS-{product.id}",
        )

    return response


# ============================================================
# OTP REGISTRATION
# ============================================================

SMS_API_KEY = config(
    "SMS_API_KEY"
)

SMS_SENDER = config(
    "SMS_SENDER"
)

SMS_MESSAGE = config(
    "SMS_MESSAGE"
)


def send_otp(mobile):

    otp = random.randint(
        100000,
        999999,
    )

    url = (
        "https://www.smsalert.co.in/"
        "api/push.json"
    )

    data = {
        "apikey": SMS_API_KEY,
        "sender": SMS_SENDER,
        "mobileno": mobile,
        "text": SMS_MESSAGE.format(
            otp=otp
        ),
    }

    try:

        requests.post(
            url,
            data=data,
            timeout=10,
        )

    except requests.RequestException as exc:

        print(
            "OTP SMS error:",
            exc,
        )

    return otp


def register(request):

    stage = "mobile"

    next_url = (
        request.GET.get("next")
        or request.POST.get("next")
    )

    if request.method == "POST":

        # ----------------------------------------------------
        # SEND OTP
        # ----------------------------------------------------

        if "send_otp" in request.POST:

            mobile = (
                request.POST.get(
                    "mobile"
                )
                or ""
            ).strip()

            if not mobile:

                messages.error(
                    request,
                    "Please enter your mobile number."
                )

                return render(
                    request,
                    "home/register.html",
                    {
                        "stage": "mobile",
                        "next_url": next_url,
                    },
                )

            otp = send_otp(
                mobile
            )

            request.session[
                "reg_mobile"
            ] = mobile

            request.session[
                "reg_otp"
            ] = otp

            request.session[
                "user_exists"
            ] = User.objects.filter(
                username=mobile
            ).exists()

            request.session[
                "login_next"
            ] = next_url

            stage = "otp"

            messages.success(
                request,
                "OTP sent successfully!"
            )

        # ----------------------------------------------------
        # VERIFY OTP
        # ----------------------------------------------------

        elif "verify_otp" in request.POST:

            entered = (
                request.POST.get(
                    "otp"
                )
                or ""
            ).strip()

            real = str(
                request.session.get(
                    "reg_otp",
                    ""
                )
            )

            mobile = request.session.get(
                "reg_mobile"
            )

            if not mobile or not real:

                messages.error(
                    request,
                    "OTP session expired. "
                    "Please request a new OTP."
                )

                return redirect(
                    "register"
                )

            if entered == real:

                if request.session.get(
                    "user_exists"
                ):

                    user = User.objects.get(
                        username=mobile
                    )

                else:

                    user = User.objects.create_user(
                        username=mobile,
                        password=mobile,
                    )

                login(
                    request,
                    user,
                )

                profile, created = (
                    Profile.objects.get_or_create(
                        user=user
                    )
                )

                profile.mobile = mobile
                profile.save(
                    update_fields=[
                        "mobile"
                    ]
                )

                next_url = request.session.get(
                    "login_next"
                )

                for key in [
                    "reg_mobile",
                    "reg_otp",
                    "user_exists",
                    "login_next",
                ]:

                    request.session.pop(
                        key,
                        None,
                    )

                if next_url:

                    return redirect(
                        next_url
                    )

                if (
                    profile.full_name
                    and profile.email
                ):

                    return redirect(
                        "product_list"
                    )

                return redirect(
                    "profile"
                )

            else:

                messages.error(
                    request,
                    "Invalid OTP."
                )

                stage = "otp"

    return render(
        request,
        "home/register.html",
        {
            "stage": stage,
            "next_url": next_url,
        },
    )


# ============================================================
# SERVICE BOOKING
# ============================================================

@login_required
def book_service(request):

    if request.method == "POST":

        form = ServiceBookingForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            booking = form.save(
                commit=False
            )

            booking.user = request.user

            prices = {
                "cctvrepair": Decimal("2000.00"),
                "computerrepair": Decimal("1000.00"),
            }

            booking.amount = prices.get(
                booking.service_type,
                Decimal("0.00"),
            )

            booking.save()

            return redirect(
                "booking_payment",
                booking_id=booking.id,
            )

    else:

        form = ServiceBookingForm()

    return render(
        request,
        "home/servicebooking.html",
        {
            "form": form,
        },
    )


# ============================================================
# SERVICE BOOKING PAYMENT
# ============================================================

@login_required
def booking_payment(
    request,
    booking_id,
):

    booking = get_object_or_404(
        ServiceBooking,
        id=booking_id,
        user=request.user,
    )

    if booking.payment_status == "paid":

        return redirect(
            "my_bookings"
        )

    if booking.amount is None or booking.amount <= 0:

        messages.error(
            request,
            "Invalid booking amount."
        )

        return redirect(
            "my_bookings"
        )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    try:

        payment = client.order.create(
            {
                "amount": int(
                    Decimal(
                        booking.amount
                    ) * 100
                ),
                "currency": "INR",
                "payment_capture": 1,
            }
        )

    except Exception as exc:

        print(
            "Booking Razorpay error:",
            exc,
        )

        messages.error(
            request,
            "Unable to initiate payment. "
            "Please try again."
        )

        return redirect(
            "my_bookings"
        )

    booking.razorpay_order_id = (
        payment["id"]
    )

    booking.save(
        update_fields=[
            "razorpay_order_id"
        ]
    )

    return render(
        request,
        "home/booking_payment.html",
        {
            "booking": booking,
            "razorpay_order_id": payment["id"],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        },
    )


# ============================================================
# SERVICE BOOKING PAYMENT SUCCESS
# ============================================================

@csrf_exempt
@require_POST
@login_required
def booking_payment_success(
    request,
    booking_id,
):

    booking = get_object_or_404(
        ServiceBooking,
        id=booking_id,
        user=request.user,
    )

    payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    order_id = request.POST.get(
        "razorpay_order_id"
    )

    signature = request.POST.get(
        "razorpay_signature"
    )

    if not all(
        [
            payment_id,
            order_id,
            signature,
        ]
    ):

        return render(
            request,
            "home/payment_failed.html",
            {
                "booking": booking,
                "error":
                    "Missing payment details."
            },
        )

    # Make sure this Razorpay order belongs
    # to this booking.
    if booking.razorpay_order_id != order_id:

        return render(
            request,
            "home/payment_failed.html",
            {
                "booking": booking,
                "error":
                    "Invalid payment order."
            },
        )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    try:

        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )

    except razorpay.errors.SignatureVerificationError:

        return render(
            request,
            "home/payment_failed.html",
            {
                "booking": booking,
                "error":
                    "Payment verification failed."
            },
        )

    booking.payment_status = "paid"
    booking.razorpay_payment_id = payment_id
    booking.razorpay_order_id = order_id

    booking.save(
        update_fields=[
            "payment_status",
            "razorpay_payment_id",
            "razorpay_order_id",
        ]
    )

    messages.success(
        request,
        "Service booking payment successful."
    )

    return render(
        request,
        "home/payment_success.html",
        {
            "booking": booking,
        },
    )


# ============================================================
# MY BOOKINGS
# ============================================================

@login_required
def my_bookings(request):

    bookings = (
        ServiceBooking.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "home/my_bookings.html",
        {
            "bookings": bookings,
        },
    )


# ============================================================
# CANCEL BOOKING
# ============================================================

# @login_required
# @require_POST
# def cancel_booking(
#     request,
#     booking_id,
# ):

#     booking = get_object_or_404(
#         ServiceBooking,
#         id=booking_id,
#         user=request.user,
#     )

#     if booking.status == "Cancelled":

#         messages.info(
#             request,
#             "This booking is already cancelled."
#         )

#         return redirect(
#             "my_bookings"
#         )

#     booking.status = "Cancelled"

#     booking.save(
#         update_fields=[
#             "status"
#         ]
#     )

#     messages.success(
#         request,
#         "Booking cancelled successfully."
#     )

#     return redirect(
#         "my_bookings"
#     )

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

@login_required
def cancel_booking(request, booking_id):

    if request.method != "POST":
        return redirect("home")

    booking = get_object_or_404(
        ServiceBooking,
        id=booking_id,
        user=request.user
    )

    booking.status = "Cancelled"
    booking.save(update_fields=["status"])

    messages.success(
        request,
        "Your booking has been cancelled successfully."
    )

    return redirect("your_booking")
# ============================================================
# STAFF DASHBOARD
# ============================================================

@staff_member_required
def staff_dashboard(request):

    cameras = Camera.objects.all()
    dvrs = DVR.objects.all()
    cables = Cable.objects.all()
    powers = PowerSupply.objects.all()
    accessories = Accessory.objects.all()
    installs = InstallationCharge.objects.all()
    combos = ComboProduct.objects.all()

    return render(
        request,
        "shop/manage/dashboard.html",
        {
            "cameras": cameras,
            "dvrs": dvrs,
            "cables": cables,
            "powers": powers,
            "accessories": accessories,
            "installs": installs,
            "combos": combos,
        },
    )


# ============================================================
# CAMERA CRUD
# ============================================================

@staff_member_required
def add_camera(request):

    if request.method == "POST":

        form = CameraForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "staff_dashboard"
            )

    else:

        form = CameraForm()

    return render(
        request,
        "shop/manage/form.html",
        {
            "form": form,
            "title": "Add Camera",
        },
    )


@staff_member_required
def edit_camera(
    request,
    pk,
):

    obj = get_object_or_404(
        Camera,
        pk=pk,
    )

    if request.method == "POST":

        form = CameraForm(
            request.POST,
            instance=obj,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "staff_dashboard"
            )

    else:

        form = CameraForm(
            instance=obj
        )

    return render(
        request,
        "shop/manage/form.html",
        {
            "form": form,
            "title": "Edit Camera",
        },
    )


@staff_member_required
def delete_camera(
    request,
    pk,
):

    obj = get_object_or_404(
        Camera,
        pk=pk,
    )

    if request.method == "POST":

        obj.delete()

        return redirect(
            "staff_dashboard"
        )

    return render(
        request,
        "shop/manage/confirm_delete.html",
        {
            "object": obj,
            "title": "Delete Camera",
        },
    )


# ============================================================
# COMBO CRUD
# ============================================================

@staff_member_required
def add_combo(request):

    if request.method == "POST":

        form = ComboForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "staff_dashboard"
            )

    else:

        form = ComboForm()

    return render(
        request,
        "shop/manage/form.html",
        {
            "form": form,
            "title": "Add Combo",
        },
    )


@staff_member_required
def edit_combo(
    request,
    pk,
):

    obj = get_object_or_404(
        ComboProduct,
        pk=pk,
    )

    if request.method == "POST":

        form = ComboForm(
            request.POST,
            instance=obj,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "staff_dashboard"
            )

    else:

        form = ComboForm(
            instance=obj
        )

    return render(
        request,
        "shop/manage/form.html",
        {
            "form": form,
            "title": "Edit Combo",
        },
    )


@staff_member_required
def delete_combo(
    request,
    pk,
):

    obj = get_object_or_404(
        ComboProduct,
        pk=pk,
    )

    if request.method == "POST":

        obj.delete()

        return redirect(
            "staff_dashboard"
        )

    return render(
        request,
        "shop/manage/confirm_delete.html",
        {
            "object": obj,
            "title": "Delete Combo",
        },
    )


# ============================================================
# BOOKING ADMIN / STAFF LIST
# ============================================================

def superuser_required(user):

    return (
        user.is_authenticated
        and user.is_superuser
    )


@login_required
@user_passes_test(
    superuser_required
)
def booking_list(request):

    bookings = (
        ServiceBooking.objects
        .select_related("user")
        .order_by("-created_at")
    )

    return render(
        request,
        "home/bookings_page.html",
        {
            "bookings": bookings,
        },
    )


# ============================================================
# CCTV ENGINEER REGISTRATION
# ============================================================

def engineer_register(request):

    message = None

    if request.method == "POST":

        form = CCTVEngineerForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            engineer = form.save()

            # ------------------------------------------------
            # ADMIN EMAIL
            # ------------------------------------------------

            admin_subject = (
                "New CCTV Engineer Registration - Camura.in"
            )

            admin_body = f"""
A new CCTV engineer has registered on Camura.in

Name: {engineer.full_name}
Mobile: {engineer.mobile}
Email: {engineer.email}
Experience: {engineer.experience}
City: {engineer.city}
Certified: {"Yes" if engineer.certified else "No"}

Address:
{engineer.address}

Login to admin panel to view full details and identity proof.
"""

            send_mail(
                admin_subject,
                admin_body,
                settings.DEFAULT_FROM_EMAIL,
                [
                    settings.ADMIN_NOTIFICATION_EMAIL
                ],
                fail_silently=False,
            )

            # ------------------------------------------------
            # ENGINEER EMAIL
            # ------------------------------------------------

            engineer_subject = (
                "Registration Successful - Camura.in"
            )

            engineer_body = f"""
Hello {engineer.full_name},

Thank you for registering as a CCTV Installation Engineer on Camura.in.

Our team will contact you shortly to verify your details and activate your profile.

Your submitted details:
----------------------------------
Name: {engineer.full_name}
Mobile: {engineer.mobile}
Email: {engineer.email}
City: {engineer.city}
Experience: {engineer.experience}
Certified: {"Yes" if engineer.certified else "No"}
----------------------------------

Thank you,
Team Camura.in
"""

            send_mail(
                engineer_subject,
                engineer_body,
                settings.DEFAULT_FROM_EMAIL,
                [
                    engineer.email
                ],
                fail_silently=False,
            )

            # ------------------------------------------------
            # SMS
            # ------------------------------------------------

            try:

                api_url = (
                    "https://www.smsalert.co.in/"
                    "api/push.json"
                )

                sms_message = (
                    f"Hi {engineer.full_name}, "
                    "your registration as CCTV "
                    "Instalation Engineer is received. "
                    "Our team will contact you to verify "
                    "your details. Thanks regards camura.in"
                )

                payload = {
                    "apikey": settings.SMS_API_KEY,
                    "sender": settings.SMS_SENDER,
                    "mobileno": engineer.mobile,
                    "text": sms_message,
                }

                requests.post(
                    api_url,
                    data=payload,
                    timeout=10,
                )

            except Exception as exc:

                print(
                    "SMS Error:",
                    exc,
                )

            message = (
                "Registration successful! "
                "Confirmation email and SMS have been sent."
            )

            form = CCTVEngineerForm()

    else:

        form = CCTVEngineerForm()

    return render(
        request,
        "home/engineer_register.html",
        {
            "form": form,
            "message": message,
        },
    )



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Order






from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import CCTVEngineer


@login_required
def registered_engineers(request):
    if not request.user.is_superuser:
        return redirect("home")

    status = request.GET.get("status", "all")

    valid_statuses = dict(CCTVEngineer.STATUS_CHOICES)

    if status != "all" and status not in valid_statuses:
        status = "all"

    engineers = CCTVEngineer.objects.all().order_by("-date_registered")

    if status != "all":
        engineers = engineers.filter(status=status)

    status_counts = {
        "all": CCTVEngineer.objects.count(),
        "pending": CCTVEngineer.objects.filter(status="pending").count(),
        "verified": CCTVEngineer.objects.filter(status="verified").count(),
        "hold": CCTVEngineer.objects.filter(status="hold").count(),
    }

    return render(
        request,
        "home/registered_engineers.html",
        {
            "engineers": engineers,
            "status": status,
            "status_counts": status_counts,
            "status_choices": CCTVEngineer.STATUS_CHOICES,
        },
    )


@login_required
@require_POST
def update_engineer_status(request, engineer_id):
    if not request.user.is_superuser:
        return redirect("home")

    engineer = get_object_or_404(CCTVEngineer, id=engineer_id)

    new_status = request.POST.get("status")
    valid_statuses = dict(CCTVEngineer.STATUS_CHOICES)

    if new_status not in valid_statuses:
        messages.error(request, "Invalid engineer status.")
        return redirect("registered_engineers")

    engineer.status = new_status
    engineer.save(update_fields=["status"])

    messages.success(
        request,
        f"{engineer.full_name}'s status updated to {valid_statuses[new_status]}."
    )

    return redirect("registered_engineers")






# @login_required
# def admin_orders(request):

#     # Only superuser can access
#     if not request.user.is_superuser:
#         return redirect("home")

#     orders = (
#         Order.objects
#         .select_related("user", "profile")
#         .prefetch_related("items")
#         .order_by("-created_at")
#     )

#     return render(
#         request,
#         "home/admin_orders.html",
#         {
#             "orders": orders,
#             "order_status_choices": Order.ORDER_STATUS_CHOICES,

#         }
#     )
    
    
    
@login_required
def admin_orders(request):
    if not request.user.is_superuser:
        return redirect("home")

    status = request.GET.get("status", "all")

    orders = (
        Order.objects
        .select_related("user", "profile")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    if status != "all":
        orders = orders.filter(order_status=status)

    status_counts = {
        "all": Order.objects.count(),
        "Received": Order.objects.filter(order_status="Received").count(),
        "Processing": Order.objects.filter(order_status="Processing").count(),
        "Shipped": Order.objects.filter(order_status="Shipped").count(),
        "Delivered": Order.objects.filter(order_status="Delivered").count(),
        "Cancelled": Order.objects.filter(order_status="Cancelled").count(),
    }

    return render(
        request,
        "home/admin_orders.html",
        {
            "orders": orders,
            "order_status_choices": Order.ORDER_STATUS_CHOICES,
            "status": status,
            "status_counts": status_counts,
        }
    )    


@login_required
@require_POST
def update_order_status(request, order_id):

    if not request.user.is_superuser:
        return redirect("home")

    order = get_object_or_404(
        Order,
        id=order_id
    )

    new_status = request.POST.get("order_status")

    valid_statuses = dict(
        Order.ORDER_STATUS_CHOICES
    )

    if new_status not in valid_statuses:
        messages.error(
            request,
            "Invalid order status."
        )

        return redirect("admin_orders")

    order.order_status = new_status
    order.save(
        update_fields=["order_status"]
    )

    messages.success(
        request,
        f"Order #{order.id} status updated to {new_status}."
    )

    return redirect("admin_orders")







from django.shortcuts import render
from .models import JobOpening


def careers(request):
    jobs = JobOpening.objects.filter(is_active=True).order_by("-created_at")

    return render(request, "home/careers.html", {"jobs": jobs})