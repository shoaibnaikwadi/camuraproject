
# ============================================================
# IMPORTS
# ============================================================

import csv
from decimal import Decimal, ROUND_HALF_UP

import razorpay

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .stock import deduct_order_stock
from affiliates.services import attach_referral_to_order
from .models import (
    Order,
    OrderItem,
    CartItem,
    Product,
    CustomerProfile,
    Profile,
    ServiceBooking,
    CCTVEngineer,
    JobOpening,
)

from .forms import (
    CustomerProfileForm,
    ServiceBookingForm,
    CCTVEngineerForm,
)


# ============================================================
# HELPERS
# ============================================================

def get_razorpay_client():
    """Create the Razorpay client using Django settings."""
    key_id = getattr(settings, "RAZORPAY_KEY_ID", "")
    key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")

    if not key_id or not key_secret:
        raise ValueError("Razorpay credentials are not configured.")

    return razorpay.Client(auth=(key_id, key_secret))


def money_to_paise(amount):
    """Convert a decimal rupee amount to integer paise."""
    amount = Decimal(str(amount))

    return int(
        (amount * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


def get_cart_items(user):
    return list(
        CartItem.objects
        .filter(user=user)
        .select_related("product")
        .order_by("-id")
    )


def get_cart_total(cart_items):
    return sum(
        (
            Decimal(str(item.product.price)) * item.quantity
            for item in cart_items
        ),
        Decimal("0.00"),
    )


def create_order_items(order, items):
    """Copy product details into order-item snapshots."""
    for item in items:
        product = item.product

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            product_details={
                "product_type": product.product_type,
                "description": product.description or "",
            },
            quantity=item.quantity,
            price=product.price,
        )


def get_or_create_user_profile(user):
    return Profile.objects.get_or_create(user=user)[0]


# ============================================================
# HOME
# ============================================================

# def home(request):
#     return render(request, "home/index.html")

from django.shortcuts import render
from .models import Product

from django.shortcuts import render
from .models import Product


def home(request):
    active_products = Product.objects.filter(
        is_active=True
    )

    latest_products = active_products.order_by(
        "-created_at"
    )[:10]

    four_camera_kits = active_products.filter(
        product_type="combo",
        camera_quantity=4,
    ).order_by("-created_at")[:10]

    three_camera_kits = active_products.filter(
        product_type="combo",
        camera_quantity=3,
    ).order_by("-created_at")[:10]

    return render(
        request,
        "home/index.html",
        {
            "latest_products": latest_products,
            "four_camera_kits": four_camera_kits,
            "three_camera_kits": three_camera_kits,
        },
    )

# ============================================================
# SEND OTP
# ============================================================
import random
import requests
from decouple import config


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

# ============================================================
# REGISTRATION
# ============================================================

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
# PRODUCT LIST
# ============================================================

# def product_list(request):
#     if request.user.is_authenticated:
#         profile = get_or_create_user_profile(request.user)

#         if not profile.full_name or not profile.email:
#             return redirect("profile")

#     combos = Product.objects.filter(
#         product_type="combo",
#         is_active=True,
#     ).order_by("-created_at")

#     products = Product.objects.filter(
#         product_type="single",
#         is_active=True,
#     ).order_by("-created_at")

#     return render(
#         request,
#         "home/product_list.html",
#         {
#             "combos": combos,
#             "products": products,
#         },
#     )








# Keep your existing import for get_or_create_user_profile.


# def product_list(request):
#     # Require users to complete their profile.
#     if request.user.is_authenticated:
#         profile = get_or_create_user_profile(request.user)

#         if not profile.full_name or not profile.email:
#             return redirect("profile")

#     # --------------------------------------------------
#     # 1. Get active combo kits
#     # --------------------------------------------------
#     combos = Product.objects.filter(
#         product_type=Product.ProductType.COMBO,
#         is_active=True,
#     ).select_related("category")

#     # --------------------------------------------------
#     # 2. Filter combos by brand
#     # --------------------------------------------------
#     brand = request.GET.get("brand", "").strip()

#     if brand:
#         combos = combos.filter(brand__iexact=brand)

#     # --------------------------------------------------
#     # 3. Filter combos by camera technology: HD or IP
#     # --------------------------------------------------
#     camera_type = request.GET.get("camera_type", "").strip()

#     valid_camera_types = dict(Product.CameraType.choices)

#     if camera_type in valid_camera_types:
#         combos = combos.filter(camera_type=camera_type)
#     else:
#         camera_type = ""

#     # --------------------------------------------------
#     # 4. Filter by camera quantity
#     # --------------------------------------------------
#     camera_quantity = request.GET.get(
#         "camera_quantity", ""
#     ).strip()

#     if camera_quantity.isdigit() and int(camera_quantity) > 0:
#         combos = combos.filter(
#             camera_quantity=int(camera_quantity)
#         )
#     else:
#         camera_quantity = ""

#     # --------------------------------------------------
#     # 5. Sort combo kits
#     # --------------------------------------------------
#     sort = request.GET.get("sort", "newest")

#     sort_options = {
#         "newest": ("-created_at",),
#         "oldest": ("created_at",),
#         "quantity_low": ("camera_quantity", "name"),
#         "quantity_high": ("-camera_quantity", "name"),
#         "brand_asc": ("brand", "name"),
#         "brand_desc": ("-brand", "name"),
#         "type_asc": ("camera_type", "name"),
#         "price_low": ("price", "name"),
#         "price_high": ("-price", "name"),
#         "name_asc": ("name",),
#         "name_desc": ("-name",),
#     }

#     if sort not in sort_options:
#         sort = "newest"

#     combos = combos.order_by(*sort_options[sort])

#     # --------------------------------------------------
#     # 6. Get available brands for the filter dropdown
#     # --------------------------------------------------
#     brands = (
#         Product.objects.filter(
#             product_type=Product.ProductType.COMBO,
#             is_active=True,
#         )
#         .exclude(brand="")
#         .values_list("brand", flat=True)
#         .distinct()
#         .order_by("brand")
#     )

#     # --------------------------------------------------
#     # 7. Get individual products
#     # --------------------------------------------------
#     products = Product.objects.filter(
#         product_type=Product.ProductType.SINGLE,
#         is_active=True,
#     ).order_by("-created_at")

#     # --------------------------------------------------
#     # 8. Render the product listing page
#     # --------------------------------------------------
#     return render(
#         request,
#         "home/product_list.html",
#         {
#             "combos": combos,
#             "products": products,
#             "brands": brands,
#             "camera_type_choices": Product.CameraType.choices,
#             "selected_brand": brand,
#             "selected_camera_type": camera_type,
#             "selected_camera_quantity": camera_quantity,
#             "selected_sort": sort,
#         },
#     )












from django.db.models import Q
from affiliates.models import AffiliateProfile

from django.db.models import Q
from django.shortcuts import render, redirect

from home.models import Product
from affiliates.models import AffiliateProfile


def product_list(request):
    # Preserve the existing profile-completion check.
    if request.user.is_authenticated:
        profile = get_or_create_user_profile(request.user)

        if not profile.full_name or not profile.email:
            return redirect("profile")

    # Only active combo kits.
    combos = Product.objects.filter(
        product_type=Product.ProductType.COMBO,
        is_active=True,
    ).select_related("category")

    # Search by product name, SKU, description, brand, or category.
    query = request.GET.get("q", "").strip()

    if query:
        combos = combos.filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(description__icontains=query)
            | Q(brand__icontains=query)
            | Q(category__name__icontains=query)
        )

    # Filter by brand.
    selected_brand = request.GET.get("brand", "").strip()

    if selected_brand:
        combos = combos.filter(brand__iexact=selected_brand)

    # Filter by camera type, such as HD or IP.
    selected_camera_type = request.GET.get(
        "camera_type", ""
    ).strip()

    valid_camera_types = dict(Product.CameraType.choices)

    if selected_camera_type in valid_camera_types:
        combos = combos.filter(camera_type=selected_camera_type)
    else:
        selected_camera_type = ""

    # Filter by camera quantity.
    selected_camera_quantity = request.GET.get(
        "camera_quantity", ""
    ).strip()

    if (
        selected_camera_quantity.isdigit()
        and int(selected_camera_quantity) > 0
    ):
        combos = combos.filter(
            camera_quantity=int(selected_camera_quantity)
        )
    else:
        selected_camera_quantity = ""

    # Sort combo products.
    sort_options = {
        "newest": ("-created_at",),
        "quantity_low": ("camera_quantity", "name"),
        "quantity_high": ("-camera_quantity", "name"),
        "brand_asc": ("brand", "name"),
        "brand_desc": ("-brand", "name"),
        "price_low": ("price", "name"),
        "price_high": ("-price", "name"),
        "name_asc": ("name",),
    }

    selected_sort = request.GET.get("sort", "newest")

    if selected_sort not in sort_options:
        selected_sort = "newest"

    combos = combos.order_by(*sort_options[selected_sort])

    # Brand dropdown options.
    brands = (
        Product.objects.filter(
            product_type=Product.ProductType.COMBO,
            is_active=True,
        )
        .exclude(brand="")
        .values_list("brand", flat=True)
        .distinct()
        .order_by("brand")
    )

    # Only quantities used by active combo kits.
    camera_quantities = (
        Product.objects.filter(
            product_type=Product.ProductType.COMBO,
            is_active=True,
        )
        .exclude(camera_quantity=0)
        .values_list("camera_quantity", flat=True)
        .distinct()
        .order_by("camera_quantity")
    )

    # Keep the existing individual-products context.
    products = Product.objects.filter(
        product_type=Product.ProductType.SINGLE,
        is_active=True,
    ).order_by("-created_at")

    # Only approved and enabled affiliates receive a referral code
    # for the Share buttons on this page.
    affiliate_referral_code = ""

    if request.user.is_authenticated:
        affiliate_referral_code = (
            AffiliateProfile.objects.filter(
                user=request.user,
                is_enabled=True,
            )
            .values_list("referral_code", flat=True)
            .first()
            or ""
        )

    return render(
        request,
        "home/product_list.html",
        {
            "combos": combos,
            "products": products,
            "brands": brands,
            "camera_type_choices": Product.CameraType.choices,
            "camera_quantities": camera_quantities,
            "selected_query": query,
            "selected_brand": selected_brand,
            "selected_camera_type": selected_camera_type,
            "selected_camera_quantity": selected_camera_quantity,
            "selected_sort": selected_sort,
            "affiliate_referral_code": affiliate_referral_code,
        },
    )    
    
# ============================================================
# PRODUCT DETAIL
# ============================================================

from django.shortcuts import get_object_or_404, render
from django.db.models import Q

from .models import Product


def product_detail(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True,
    )

    # Suggestions are shown only for combo/package products.
    suggested_products = Product.objects.none()

    if product.product_type == Product.ProductType.COMBO:

        # Products already included in this package.
        included_component_ids = product.components.values_list(
            "component_id",
            flat=True,
        )

        # Suggest complementary single products only.
        suggested_products = (
            Product.objects.filter(
                Q(name__icontains="rack")
                | Q(name__icontains="ups")
                | Q(name__icontains="accessory")
                | Q(category__name__icontains="accessor"),
                product_type=Product.ProductType.SINGLE,
                is_active=True,
                stock__gt=0,
            )
            .exclude(pk__in=included_component_ids)
            .select_related("category")
            .order_by("name")[:8]
        )

    return render(
        request,
        "home/product_detail.html",
        {
            "combo": product,
            "product": product,
            "price": product.price,
            "available_stock": product.available_stock,
            "suggested_products": suggested_products,
        },
    )






# ============================================================
# ACCESORIES PAGE
# ============================================================

def accessories(request):
    # Show ONLY active single products, never combo products.
    products = Product.objects.filter(
        product_type="single",
        is_active=True,
    ).select_related("category").order_by("-created_at")

    query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()

    # Search by product name, SKU, description, or category.
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    # Filter by category name.
    if selected_category:
        products = products.filter(
            category__name=selected_category
        )

    categories = (
        Product.objects.filter(
            product_type="single",
            is_active=True,
            category__isnull=False,
        )
        .values_list("category__name", flat=True)
        .distinct()
        .order_by("category__name")
    )

    return render(
        request,
        "home/accessories.html",
        {
            "products": products,
            "categories": categories,
            "query": query,
            "selected_category": selected_category,
        },
    )


def accessory_suggestions(request):
    query = request.GET.get("q", "").strip()

    suggestions = []

    if len(query) >= 2:
        products = (
            Product.objects.filter(
                product_type="single",
                is_active=True,
            )
            .filter(
                Q(name__icontains=query)
                | Q(sku__icontains=query)
                | Q(description__icontains=query)
            )
            .select_related("category")
            .order_by("name")[:10]
        )

        suggestions = [
            {
                "name": product.name,
                "category": (
                    product.category.name
                    if product.category_id
                    else "CCTV Product"
                ),
                "model_number": product.sku or "",
            }
            for product in products
        ]

    return JsonResponse({"suggestions": suggestions})





# ============================================================
# CART
# ============================================================

@login_required
def cart(request):
    cart_items = get_cart_items(request.user)
    total = get_cart_total(cart_items)

    return render(
        request,
        "home/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
            "cart_total": total,
        },
    )

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .models import Product, CartItem


@login_required
@require_POST
def add_to_cart(request, product_type, product_id):

    # 1. Validate requested product type
    if product_type not in Product.ProductType.values:
        messages.error(request, "Invalid product type.")
        return redirect("product_list")

    # 2. Read quantity from the form
    raw_quantity = request.POST.get(
        "qty",
        request.POST.get("quantity", "1"),
    )

    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("product_list")

    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect("product_list")

    try:
        with transaction.atomic():

            # 3. Find and lock the product
            product = (
                Product.objects
                .select_for_update()
                .filter(
                    pk=product_id,
                    is_active=True,
                )
                .first()
            )

            if product is None:
                messages.error(
                    request,
                    "This product was not found or is no longer available.",
                )
                return redirect("product_list")

            # 4. Ensure the requested type matches the database record
            if product.product_type != product_type:
                messages.error(
                    request,
                    "The product type does not match. Please open the correct product page.",
                )
                return redirect("product_list")

            # 5. Check current availability
            available_stock = product.available_stock

            if available_stock < 1:
                messages.error(
                    request,
                    "This product is currently out of stock.",
                )
                return redirect("product_list")

            # 6. Find existing cart item or create one
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={"quantity": quantity},
            )

            # Add the requested quantity to an existing cart item
            if not created:
                cart_item.quantity += quantity

            # 7. Validate the requested total quantity against stock
            cart_item.full_clean()
            cart_item.save()

    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("cart")

    messages.success(
        request,
        f"{product.name} added to your cart successfully.",
    )

    return redirect("cart")

@login_required
@require_POST
def remove_cart_item(request, item_id):
    item = get_object_or_404(
        CartItem,
        pk=item_id,
        user=request.user,
    )

    item.delete()

    messages.success(request, "Item removed from your cart.")
    return redirect("cart")


@login_required
@require_POST
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()

    messages.success(request, "Your cart has been cleared.")
    return redirect("cart")





@login_required
@require_POST
def update_cart_quantity(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user,
    )

    action = request.POST.get("action")

    if action == "increase":
        if item.quantity < item.available_stock:
            item.quantity += 1
            item.save(update_fields=["quantity"])
            messages.success(request, "Cart quantity updated.")
        else:
            messages.warning(request, "You cannot add more than the available stock.")

    elif action == "decrease":
        if item.quantity > 1:
            item.quantity -= 1
            item.save(update_fields=["quantity"])
            messages.success(request, "Cart quantity updated.")
        else:
            messages.info(request, "Minimum quantity is 1.")

    return redirect("cart")
# ============================================================
# SELECT ADDRESS
# ============================================================

from decimal import Decimal
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import CustomerProfile, Product

# Keep your existing import for get_cart_items.


@login_required
def select_address(request):

    # =====================================================
    # 1. DETERMINE CHECKOUT SOURCE
    # =====================================================

    from_page = (
        request.POST.get("from")
        or request.GET.get("from")
        or request.session.get("checkout_from")
        or ""
    ).strip().lower()

    # Preserve both cart checkout and Buy Now.
    if from_page not in ("cart", "buy_now"):
        if (
            request.session.get("buy_now_product_id")
            or request.session.get("buy_now_combo_id")
        ):
            from_page = "buy_now"
        else:
            from_page = "cart"

    request.session["checkout_from"] = from_page

    # =====================================================
    # 2. PRESERVE BUY NOW PRODUCT ID
    # =====================================================

    combo_id = (
        request.session.get("buy_now_product_id")
        or request.session.get("buy_now_combo_id")
        or request.POST.get("combo_id")
        or request.GET.get("combo_id")
        or ""
    )

    # For Buy Now, use the saved session product ID as the
    # authoritative ID, rather than trusting a form value.
    buy_now_product = None

    if from_page == "buy_now":

        if not combo_id:
            messages.error(
                request,
                "Your Buy Now session has expired. Please select the product again.",
            )
            return redirect("product_list")

        buy_now_product = get_object_or_404(
            Product,
            pk=combo_id,
            is_active=True,
        )

        # Support both the current and older session key.
        request.session["buy_now_product_id"] = buy_now_product.pk
        request.session["buy_now_combo_id"] = buy_now_product.pk
        combo_id = buy_now_product.pk

        # Preserve the requested quantity from Buy Now.
        try:
            buy_now_quantity = int(
                request.session.get("buy_now_quantity", 1)
            )
        except (TypeError, ValueError):
            buy_now_quantity = 1

        if buy_now_quantity < 1:
            buy_now_quantity = 1

        request.session["buy_now_quantity"] = buy_now_quantity

    # =====================================================
    # 3. ADDRESS PAGE REDIRECT HELPER
    # =====================================================

    def return_to_address_page():
        params = {"from": from_page}

        if combo_id:
            params["combo_id"] = combo_id

        query_string = urlencode(params)

        return redirect(
            f"{reverse('select_address')}?{query_string}"
        )

    # =====================================================
    # 4. HANDLE POST REQUESTS
    # =====================================================

    if request.method == "POST":

        address_id = request.POST.get("address_id")

        # ---------------------------------------------
        # SELECT AN EXISTING ADDRESS
        # ---------------------------------------------

        if address_id:

            address = get_object_or_404(
                CustomerProfile,
                pk=address_id,
                user=request.user,
            )

            request.session["selected_address_id"] = address.pk
            request.session["checkout_from"] = from_page
            request.session.modified = True

            messages.success(
                request,
                "Delivery address selected successfully.",
            )

            # IMPORTANT:
            # Return to the address page. The customer can
            # then click the correct Continue button.
            #
            # Buy Now -> process_buy_now
            # Cart    -> cart_checkout
            return return_to_address_page()

        # ---------------------------------------------
        # SAVE A NEW ADDRESS
        # ---------------------------------------------

        required_fields = (
            "full_name",
            "email",
            "mobile",
            "pincode",
            "address",
            "city",
            "state",
        )

        values = {
            field: (request.POST.get(field) or "").strip()
            for field in required_fields
        }

        if not all(values.values()):

            messages.error(
                request,
                "Please fill in all address fields.",
            )

        else:

            new_address = CustomerProfile.objects.create(
                user=request.user,
                **values,
            )

            request.session["selected_address_id"] = new_address.pk
            request.session["checkout_from"] = from_page
            request.session.modified = True

            messages.success(
                request,
                "Address added successfully.",
            )

            return return_to_address_page()

    # =====================================================
    # 5. LOAD SAVED ADDRESSES
    # =====================================================

    addresses = CustomerProfile.objects.filter(
        user=request.user,
    ).order_by("-id")

    selected_address_id = request.session.get(
        "selected_address_id"
    )

    # If no valid saved address is selected, choose the
    # most recent address as the default.
    if not addresses.filter(pk=selected_address_id).exists():

        first_address = addresses.first()

        if first_address:
            selected_address_id = first_address.pk
            request.session["selected_address_id"] = first_address.pk
        else:
            selected_address_id = None
            request.session.pop("selected_address_id", None)

        request.session.modified = True

    # =====================================================
    # 6. BUILD ORDER SUMMARY
    # =====================================================

    items = []
    total = Decimal("0.00")

    if from_page == "buy_now" and buy_now_product:

        quantity = request.session.get("buy_now_quantity", 1)

        unit_price = Decimal(str(buy_now_product.price))
        subtotal = unit_price * quantity

        items.append({
            "name": buy_now_product.name,
            "qty": quantity,
            "price": unit_price,
            "subtotal": subtotal,
        })

        total = subtotal

    else:

        cart_items = get_cart_items(request.user)

        for item in cart_items:

            unit_price = Decimal(str(item.product.price))
            subtotal = unit_price * item.quantity

            items.append({
                "name": item.product.name,
                "qty": item.quantity,
                "price": unit_price,
                "subtotal": subtotal,
            })

            total += subtotal

    # =====================================================
    # 7. RENDER ADDRESS PAGE
    # =====================================================

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
def delete_address(request, id):
    address = get_object_or_404(
        CustomerProfile,
        pk=id,
        user=request.user,
    )

    selected_address_id = request.session.get("selected_address_id")
    address.delete()

    if selected_address_id == id:
        next_address = (
            CustomerProfile.objects
            .filter(user=request.user)
            .order_by("-id")
            .first()
        )

        if next_address:
            request.session["selected_address_id"] = next_address.pk
        else:
            request.session.pop("selected_address_id", None)

    messages.success(request, "Address deleted successfully.")
    return redirect("select_address")


# ============================================================
# CHECKOUT - ONLINE PAYMENT
# ============================================================
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST




@login_required
@require_POST
def cart_checkout(request):
    # 1. Get the selected delivery address
    address_id = request.session.get("selected_address_id")

    if not address_id:
        messages.error(request, "Please select a delivery address.")
        return redirect("select_address")

    profile = CustomerProfile.objects.filter(
        pk=address_id,
        user=request.user,
    ).first()

    if not profile:
        request.session.pop("selected_address_id", None)
        messages.error(
            request,
            "Your selected delivery address was not found. Please select an address again.",
        )
        return redirect("select_address")

    # 2. Get cart items
    cart_items = list(get_cart_items(request.user))

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    try:
        with transaction.atomic():

            # 3. Lock and validate each product
            for item in cart_items:
                product = Product.objects.select_for_update().filter(
                    pk=item.product_id,
                    is_active=True,
                ).first()

                if product is None:
                    messages.error(
                        request,
                        f"{item.product_name} is no longer available.",
                    )
                    return redirect("cart")

                item.product = product
                item.full_clean()

            # 4. Calculate the current cart total
            total = get_cart_total(cart_items)

            # 5. Enforce the minimum order requirement
            # Your requirement is MORE THAN ₹5,000.
            if total <= Decimal("5000.00"):
                messages.error(
                    request,
                    "Your order total must exceed ₹5,000 to proceed.",
                )
                return redirect("cart")

            if total <= 0:
                messages.error(request, "The order total must be positive.")
                return redirect("cart")

            # 6. Create the local order
            order = Order.objects.create(
                user=request.user,
                profile=profile,
                total_amount=total,
                payment_method="online",
                payment_status="Pending",
            )

            create_order_items(order, cart_items)

            # 7. Create Razorpay order
            amount_paise = money_to_paise(total)
            client = get_razorpay_client()

            payment = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "receipt": str(order.pk),
            })

            # 8. Save Razorpay order ID
            order.razorpay_order_id = payment["id"]
            order.save(update_fields=["razorpay_order_id"])

    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("cart")

    except Exception:
        # Log the actual exception in your server logs when debugging.
        messages.error(
            request,
            "Unable to initiate online payment. Please try again.",
        )
        return redirect("cart")

    # 9. Display the online payment page
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
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Product, CustomerProfile, Order, OrderItem

# Keep your existing money_to_paise and get_razorpay_client imports.


@login_required
@require_POST
def buy_now(request, combo_id):
    """
    Start a Buy Now purchase for either an individual product
    or a combo kit. The existing URL parameter is named combo_id,
    but it contains a Product primary key for both product types.
    """
    product = get_object_or_404(
        Product,
        pk=combo_id,
        is_active=True,
    )

    raw_quantity = request.POST.get(
        "qty",
        request.POST.get("quantity", "1"),
    )

    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("product_detail", pk=product.pk)

    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect("product_detail", pk=product.pk)

    available_stock = product.available_stock

    if available_stock < 1:
        messages.error(request, "This product is out of stock.")
        return redirect("product_detail", pk=product.pk)

    if quantity > available_stock:
        messages.error(
            request,
            f"Only {available_stock} unit(s) are currently available.",
        )
        return redirect("product_detail", pk=product.pk)

    # Save the selected product and quantity for the address/payment flow.
    request.session["buy_now_product_id"] = product.pk
    request.session["buy_now_quantity"] = quantity

    # Remove keys used by an older implementation, if present.
    request.session.pop("buy_now_combo_id", None)
    request.session.modified = True

    return redirect(
        f"{reverse('select_address')}?from=buy_now&combo_id={product.pk}"
    )


@login_required
@require_POST
def process_buy_now(request, combo_id):
    """
    Create an order for the product selected through Buy Now,
    then display the existing Razorpay/COD payment page.
    """
    product_id = request.session.get("buy_now_product_id")
    quantity = request.session.get("buy_now_quantity", 1)

    # Require a matching Buy Now session so a stale or unrelated URL
    # cannot accidentally purchase another product.
    if not product_id or str(product_id) != str(combo_id):
        messages.error(
            request,
            "Your Buy Now session has expired. Please select the product again.",
        )
        return redirect("product_detail", pk=combo_id)

    address_id = request.session.get("selected_address_id")

    if not address_id:
        return redirect(
            f"{reverse('select_address')}?from=buy_now&combo_id={combo_id}"
        )

    profile = CustomerProfile.objects.filter(
        pk=address_id,
        user=request.user,
    ).first()

    if profile is None:
        request.session.pop("selected_address_id", None)
        messages.error(request, "Please select a valid delivery address.")
        return redirect(
            f"{reverse('select_address')}?from=buy_now&combo_id={combo_id}"
        )

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        messages.error(request, "Invalid purchase quantity.")
        return redirect("product_detail", pk=combo_id)

    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect("product_detail", pk=combo_id)

    try:
        with transaction.atomic():

            product = (
                Product.objects
                .select_for_update()
                .filter(
                    pk=combo_id,
                    is_active=True,
                )
                .first()
            )

            if product is None:
                messages.error(
                    request,
                    "This product is no longer available.",
                )
                return redirect("product_list")

            # Recheck stock immediately before creating the order.
            available_stock = product.available_stock

            if available_stock < 1:
                messages.error(request, "This product is out of stock.")
                return redirect("product_detail", pk=product.pk)

            if quantity > available_stock:
                messages.error(
                    request,
                    f"Only {available_stock} unit(s) are currently available.",
                )
                return redirect("product_detail", pk=product.pk)

            unit_price = Decimal(str(product.price))
            total = unit_price * quantity

            if total <= 0:
                messages.error(request, "Invalid product price.")
                return redirect("product_detail", pk=product.pk)

            # Create the order for the requested quantity.
            order = Order.objects.create(
                user=request.user,
                profile=profile,
                total_amount=total,
                payment_method="online",
                payment_status="Pending",
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_sku=product.sku,
                product_details={
                    "product_type": product.product_type,
                    "description": product.description or "",
                },
                quantity=quantity,
                price=unit_price,
            )

            # Initiate Razorpay payment.
            amount_paise = money_to_paise(total)
            client = get_razorpay_client()

            payment = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "receipt": str(order.pk),
            })

            order.razorpay_order_id = payment["id"]
            order.save(update_fields=["razorpay_order_id"])

    except Exception:
        # The transaction rolls back local order changes on failure.
        # Check the Django terminal logs for the underlying exception.
        messages.error(
            request,
            "Unable to create your order or initiate payment. "
            "Please try again.",
        )
        return redirect("product_detail", pk=combo_id)

    # The order has been created, so these temporary Buy Now values
    # are no longer needed to render the payment page.
    request.session.pop("buy_now_product_id", None)
    request.session.pop("buy_now_quantity", None)
    request.session.modified = True

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
# PAYMENT SUCCESS / VERIFICATION
# ============================================================




@csrf_exempt
@require_POST
def payment_success(request):
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    # --------------------------------------------------
    # 1. Check required Razorpay payment details
    # --------------------------------------------------
    if not all((
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature,
    )):
        return render(
            request,
            "home/payment_failed.html",
            {"error": "Missing payment details."},
        )

    # --------------------------------------------------
    # 2. Verify signature and captured payment with Razorpay
    # --------------------------------------------------
    try:
        client = get_razorpay_client()

        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })

        # A valid signature alone does not prove the payment
        # has been captured.
        payment_info = client.payment.fetch(
            razorpay_payment_id
        )

        if payment_info.get("order_id") != razorpay_order_id:
            raise ValueError(
                "Payment does not match the Razorpay order."
            )

        if payment_info.get("status") != "captured":
            return render(
                request,
                "home/payment_failed.html",
                {
                    "error": (
                        "Payment has not been captured yet. "
                        "Please contact support if money was deducted."
                    )
                },
            )

    except Exception:
        return render(
            request,
            "home/payment_failed.html",
            {
                "error": (
                    "Payment verification failed. "
                    "Please contact support if money was deducted."
                )
            },
        )

    # --------------------------------------------------
    # 3. Mark order as paid and deduct stock atomically
    # --------------------------------------------------
    stock_error = None

    try:
        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update(),
                razorpay_order_id=razorpay_order_id,
                payment_method="online",
            )

            # Save payment information.
            if order.payment_status != "Paid":
                order.payment_id = razorpay_payment_id
                order.payment_status = "Paid"

                order.save(
                    update_fields=[
                        "payment_id",
                        "payment_status",
                    ]
                )

            # Deduct physical inventory only after payment verification.
            # deduct_order_stock() must handle combo components and
            # use order.stock_deducted to prevent repeat deductions.
            try:
                deduct_order_stock(order)

            except ValidationError as exc:
                # Payment is already captured. Keep the order marked
                # as paid, but report the stock problem for resolution.
                stock_error = "; ".join(exc.messages)

    except Order.DoesNotExist:
        return render(
            request,
            "home/payment_failed.html",
            {
                "error": (
                    "The paid order could not be found. "
                    "Please contact support."
                )
            },
        )

    # --------------------------------------------------
    # 4. Remove only purchased quantities from the cart
    # --------------------------------------------------
    # If stock deduction failed, preserve the cart for investigation.
    if order.user_id and not stock_error:
        purchased = {}

        for item in order.orderitem_set.all():
            if item.product_id:
                purchased[item.product_id] = (
                    purchased.get(item.product_id, 0)
                    + item.quantity
                )

        for product_id, quantity in purchased.items():
            cart_item = CartItem.objects.filter(
                user=order.user,
                product_id=product_id,
            ).first()

            if cart_item:
                if cart_item.quantity <= quantity:
                    cart_item.delete()
                else:
                    cart_item.quantity -= quantity
                    cart_item.save(update_fields=["quantity"])

    # --------------------------------------------------
    # 5. Clear checkout session details
    # --------------------------------------------------
    if request.user.is_authenticated:
        request.session.pop("selected_address_id", None)
        request.session.pop("buy_now_combo_id", None)
        request.session.pop("buy_now_product_id", None)
        request.session.pop("buy_now_quantity", None)
        request.session.pop("checkout_from", None)

    # --------------------------------------------------
    # 6. Show the correct result to the customer
    # --------------------------------------------------
    if stock_error:
        messages.warning(
            request,
            (
                "Your payment was captured, but automatic stock "
                "deduction failed. Please contact support before "
                f"the order is fulfilled. Details: {stock_error}"
            ),
        )
    else:
        messages.success(
            request,
            "Payment successful. Your order is confirmed.",
        )

    if order.user_id:
        return redirect(
            "order_success",
            order_id=order.pk,
        )

    return render(
        request,
        "home/order_success.html",
        {"order": order},
    )

# ============================================================
# COD PAYMENT
# ============================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db import transaction

# Keep your existing imports for Order and get_cart_items.


@login_required
@require_POST
def cod_payment(request):
    order_id = request.POST.get("order_id")

    if not order_id:
        messages.error(
            request,
            "Order ID is missing. Please try checkout again."
        )
        return redirect("cart")

    # Find the existing order belonging to the logged-in customer.
    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )

    # Find the actual Cash on Delivery value defined in your model.
    payment_field = Order._meta.get_field("payment_method")
    cod_value = None

    for value, label in payment_field.choices:
        value_text = str(value).strip().lower().replace("_", " ").replace("-", " ")
        label_text = str(label).strip().lower()

        if (
            value_text in {"cod", "cash", "cash on delivery"}
            or label_text in {"cod", "cash on delivery"}
            or "cash on delivery" in label_text
        ):
            cod_value = value
            break

    if cod_value is None:
        messages.error(
            request,
            "Cash on Delivery is not configured in your Order model. "
            "Please check the payment_method choices."
        )
        return redirect("cart")

    # An order already exists because cart_checkout created it.
    # Update its payment method instead of creating a duplicate.
    with transaction.atomic():
        order = Order.objects.select_for_update().get(
            pk=order.pk,
            user=request.user,
        )

        order.payment_method = cod_value

        # Keep payment_status as Pending for COD.
        # The customer pays when the order is delivered.
        order.save(update_fields=["payment_method"])
        
        attach_referral_to_order(request, order)


        # Clear the cart only after the COD order is saved.
        for cart_item in get_cart_items(request.user):
            cart_item.delete()

    messages.success(
        request,
        f"Your Cash on Delivery order {order.pk} has been placed successfully."
    )
    deduct_order_stock(order)
    

    return redirect("order_success", order_id=order.pk)


# ============================================================
# ORDER SUCCESS
# ============================================================
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Order, OrderItem


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )

    order_items = []

    for item in OrderItem.objects.filter(order=order).select_related("product"):

        unit_price = Decimal(str(item.price))
        quantity = item.quantity
        details = item.product_details or {}

        order_items.append({
            "product_name": (
                item.product_name
                or (item.product.name if item.product_id else "Product")
            ),
            "sku": (
                item.product_sku
                or (item.product.sku if item.product_id else "")
            ),
            "product_type": (
                details.get("product_type", "")
                if isinstance(details, dict)
                else ""
            ),
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": unit_price * quantity,
            "image": (
                item.product.main_image.url
                if item.product_id and item.product.main_image
                else ""
            ),
        })

    return render(
        request,
        "home/order_success.html",
        {
            "order": order,
            "order_items": order_items,
        },
    )

# ============================================================
# MY ORDERS
# ============================================================

@login_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user,
    ).order_by("-created_at")

    return render(
        request,
        "home/my_orders.html",
        {"orders": orders},
    )


# ============================================================
# PROFILE
# ============================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect

from .models import Profile


@login_required
def profile(request):
    profile_obj = get_or_create_user_profile(request.user)

    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        email = (request.POST.get("email") or "").strip()

        if not full_name:
            messages.error(request, "Full name is required.")
            return redirect("profile")

        if not email:
            messages.error(request, "Email address is required.")
            return redirect("profile")

        # Check if another user's profile already uses this email.
        email_exists = Profile.objects.filter(
            email__iexact=email
        ).exclude(
            pk=profile_obj.pk
        ).exists()

        if email_exists:
            messages.error(
                request,
                "This email address is already registered. "
                "Please use another email address."
            )
            return redirect("profile")

        try:
            with transaction.atomic():
                profile_obj.full_name = full_name
                profile_obj.email = email
                profile_obj.save()

        except IntegrityError:
            # Handles a duplicate email if another request saves it
            # between our initial check and the database save.
            messages.error(
                request,
                "This email address is already registered. "
                "Please use another email address."
            )
            return redirect("profile")

        messages.success(request, "Profile updated successfully.")
        return redirect("product_list")

    return render(
        request,
        "home/profile.html",
        {"profile": profile_obj},
    )

# ============================================================
# CUSTOMER ADDRESSES
# ============================================================

@login_required
def address_list(request):
    addresses = CustomerProfile.objects.filter(
        user=request.user,
    ).order_by("-id")

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        fields = (
            "full_name",
            "email",
            "mobile",
            "pincode",
            "address",
            "city",
            "state",
        )

        values = {
            field: (request.POST.get(field) or "").strip()
            for field in fields
        }

        if not all(values.values()):
            messages.error(request, "Please fill in all address fields.")
            return redirect("address_list")

        if form_type == "add":
            CustomerProfile.objects.create(
                user=request.user,
                **values,
            )

            messages.success(request, "Address added successfully.")
            return redirect("address_list")

        if form_type == "edit":
            address = get_object_or_404(
                CustomerProfile,
                pk=request.POST.get("address_id"),
                user=request.user,
            )

            for field, value in values.items():
                setattr(address, field, value)

            address.save()

            messages.success(request, "Address updated successfully.")
            return redirect("address_list")

    return render(
        request,
        "home/addresses.html",
        {"addresses": addresses},
    )


@login_required
@require_POST
def delete_address_from_list(request, id):
    address = get_object_or_404(
        CustomerProfile,
        pk=id,
        user=request.user,
    )

    selected_address_id = request.session.get("selected_address_id")
    address.delete()

    if selected_address_id == id:
        request.session.pop("selected_address_id", None)

    messages.success(request, "Address deleted.")
    return redirect("address_list")


# ============================================================
# CONTACT
# ============================================================

def contact_view(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        message = (request.POST.get("message") or "").strip()

        if not name or not email or not message:
            messages.error(request, "Please complete all contact fields.")
            return redirect("contact")

        try:
            send_mail(
                subject=f"New Contact Message from {name}",
                message=(
                    f"Name: {name}\n"
                    f"Email: {email}\n\n"
                    f"Message:\n{message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            messages.success(
                request,
                "Thank you for contacting us. We will get back to you soon.",
            )

        except Exception:
            messages.error(
                request,
                "Your message could not be sent. Please try again later.",
            )

        return redirect("contact")

    return render(request, "home/contact.html")


# ============================================================
# INFORMATION PAGES
# ============================================================

def privacy_policy(request):
    return render(request, "home/privacy_policy.html")


def shipping_policy(request):
    return render(request, "home/shipping_policy.html")


def warranty(request):
    return render(request, "home/warranty.html")


def terms_and_conditions(request):
    return render(request, "home/terms_and_conditions.html")


def refund_cancellation_policy(request):
    return render(request, "home/refund_cancellation_policy.html")


# ============================================================
# GOOGLE PRODUCT FEED
# ============================================================

def google_feed(request):
    response = HttpResponse(
        content_type="text/csv; charset=utf-8",
    )

    response["Content-Disposition"] = (
        'inline; filename="google_feed.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
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
    ])

    products = Product.objects.filter(
        is_active=True,
    ).order_by("id")

    for product in products:
        absolute_link = request.build_absolute_uri(
            reverse("product_detail", args=[product.pk])
        )

        image_link = ""

        if product.main_image:
            image_link = request.build_absolute_uri(
                product.main_image.url
            )

        availability = (
            "in stock"
            if product.available_stock > 0
            else "out of stock"
        )

        writer.writerow([
            product.pk,
            product.name,
            product.description or "",
            absolute_link,
            image_link,
            f"{Decimal(str(product.price)):.2f} INR",
            availability,
            "new",
            "Camura",
            "Electronics",
            product.sku or "",
            product.product_type,
            "",
            "no" if not product.sku else "yes",
        ])

    return response








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







def careers(request):
    jobs = JobOpening.objects.filter(is_active=True).order_by("-created_at")

    return render(request, "home/careers.html", {"jobs": jobs})



import json

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.html import escape

from .models import JobOpening


def job_detail(request, job_id):
    job = get_object_or_404(
        JobOpening,
        id=job_id,
        is_active=True
    )

    today = timezone.localdate()
    job_schema = None

    if not job.last_date or job.last_date >= today:
        description = (
            f"<p>{escape(job.description or '')}</p>"
            f"<p>Responsibilities: {escape(job.responsibilities or '')}</p>"
            f"<p>Requirements: {escape(job.requirements or '')}</p>"
            f"<p>Qualification: {escape(job.qualification or '')}</p>"
            f"<p>Experience: {escape(job.experience or '')}</p>"
        )

        schema = {
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": job.title,
            "description": description,
            "identifier": {
                "@type": "PropertyValue",
                "name": "Camura",
                "value": str(job.id),
            },
            "datePosted": job.created_at.date().isoformat(),
            "hiringOrganization": {
                "@type": "Organization",
                "name": "N S Corporation",
                "sameAs": "https://camura.in",
            },
            "jobLocation": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": job.location,
                    "addressRegion": "Maharashtra",
                    "addressCountry": "IN",
                },
            },
        }

        if job.last_date:
            schema["validThrough"] = (
                job.last_date.isoformat() + "T23:59:59+05:30"
            )

        if job.job_type:
            schema["employmentType"] = (
                job.job_type.upper().replace(" ", "_")
            )

        job_schema = json.dumps(schema)

    return render(
        request,
        "home/job_detail.html",
        {
            "job": job,
            "job_schema": job_schema,
            "today": today,
        },
    )    
    
    
    
    
    
    
    
    

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from .models import Product

