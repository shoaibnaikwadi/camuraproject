
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.html import strip_tags
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import login
from django.contrib.auth.models import User

import razorpay
import requests
import random
from decouple import config
from django.contrib.auth import get_user_model

from decimal import Decimal, ROUND_HALF_UP

MINIMUM_ORDER = Decimal("5000.00")

from .models import (
    Order, OrderItem, CartItem, ComboProduct, CustomerProfile,
    Profile, Camera, DVR, Cable, PowerSupply, Accessory, InstallationCharge
)

from .forms import (
    CustomerProfileForm, ServiceBookingForm, CameraForm, CableForm, PowerSupplyForm, AccessoryForm, InstallationForm, ComboForm )
 


# @login_required
def home(request):
    return render(request, 'home/index.html')






def registerold(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'home/registerold.html', {'form': form})







def product_list(request): 
    if request.user.is_authenticated:
        profile = request.user.profile
        if not profile.full_name or not profile.email:
            return redirect("profile")

    combos = ComboProduct.objects.all()
    return render(request, 'home/product_list.html', {'combos': combos})








def product_detail(request, pk):
    combo = get_object_or_404(ComboProduct, pk=pk)

    # Calculate discount percentage
    discount = None
    if combo.mrp and combo.mrp > combo.total_price():
        discount = round((combo.mrp - combo.total_price()) / combo.mrp * 100)

    context = {
        'combo': combo,
        'discount': discount,
    }
    return render(request, 'home/product_detail.html', context)










@login_required
def cod_payment(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order.payment_status = "COD"
        order.save()

        messages.success(request, "Order placed successfully! Pay with COD on delivery.")
        return redirect('order_success')



# STAFF MANAGEMENT VIEWS (CRUD) - protected
@staff_member_required
def staff_dashboard(request):
    cameras = Camera.objects.all()
    dvrs = DVR.objects.all()
    cables = Cable.objects.all()
    powers = PowerSupply.objects.all()
    accessories = Accessory.objects.all()
    installs = InstallationCharge.objects.all()
    combos = ComboProduct.objects.all()
    return render(request, 'shop/manage/dashboard.html', {
        'cameras': cameras,'dvrs': dvrs,'cables': cables,
        'powers': powers,'accessories': accessories,'installs': installs,'combos': combos
    })

# Generic add/edit/delete views (one pattern per model)
@staff_member_required
def add_camera(request):
    if request.method == 'POST':
        form = CameraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = CameraForm()
    return render(request, 'shop/manage/form.html', {'form': form, 'title': 'Add Camera'})

@staff_member_required
def edit_camera(request, pk):
    obj = get_object_or_404(Camera, pk=pk)
    if request.method == 'POST':
        form = CameraForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = CameraForm(instance=obj)
    return render(request, 'shop/manage/form.html', {'form': form, 'title': 'Edit Camera'})

@staff_member_required
def delete_camera(request, pk):
    obj = get_object_or_404(Camera, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('staff_dashboard')
    return render(request, 'shop/manage/confirm_delete.html', {'object': obj, 'title': 'Delete Camera'})



@staff_member_required
def add_combo(request):
    if request.method == 'POST':
        form = ComboForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = ComboForm()
    return render(request, 'shop/manage/form.html', {'form': form, 'title': 'Add Combo'})

@staff_member_required
def edit_combo(request, pk):
    obj = get_object_or_404(ComboProduct, pk=pk)
    if request.method == 'POST':
        form = ComboForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = ComboForm(instance=obj)
    return render(request, 'shop/manage/form.html', {'form': form, 'title': 'Edit Combo'})

@staff_member_required
def delete_combo(request, pk):
    obj = get_object_or_404(ComboProduct, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('staff_dashboard')
    return render(request, 'shop/manage/confirm_delete.html', {'object': obj, 'title': 'Delete Combo'})


##################################################################################
# accesories page 


from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from .models import (
    Camera, CameraBullet, DVR, HardDisk,
    Cable, PowerSupply, Accessory
)


def get_accessory_products():

    products = []

    categories = [
        (Camera, "Camera", "camera_type", "camera"),
        (
            CameraBullet, "Bullet Camera",
            "bullet_camera_type", "bullet_camera"
        ),
        (DVR, "DVR", "dvr_name", "dvr"),
        (HardDisk, "Hard Disk", "size", "hard_disk"),
        (Cable, "Cable", "length", "cable"),
        (
            PowerSupply, "Power Supply",
            "range_slug", "power_supply"
        ),
        (Accessory, "Accessory", "name", "accessory"),
    ]

    for model, category, name_field, product_type in categories:

        for item in model.objects.all():

            name = getattr(item, name_field)

            model_number = (
                getattr(item, "model_number", None)
                or getattr(item, "bullet_model_number", None)
            )

            products.append({
                "id": item.pk,
                "name": name,
                "category": category,
                "product_type": product_type,
                "model_number": model_number,
                "price": item.price,
                "stock": item.stock,
                "image": item.image,

            })

    return products

def accessories(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    products = get_accessory_products()

    if category:
        products = [
            p for p in products
            if p["category"] == category
        ]

    if query:
        products = [
            p for p in products
            if query.lower() in (
                p["name"] + " " +
                (p["model_number"] or "")
            ).lower()
        ]

    products.sort(key=lambda p: p["name"].lower())

    return render(request, "home/accessories.html", {
        "products": products,
        "query": query,
        "selected_category": category,
        "categories": [
            "Camera", "Bullet Camera", "DVR",
            "Hard Disk", "Cable", "Power Supply",
            "Accessory"
        ],
    })


def accessory_suggestions(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"suggestions": []})

    products = get_accessory_products()

    matches = [
        {
            "name": p["name"],
            "category": p["category"],
            "model_number": p["model_number"],
        }
        for p in products
        if query.lower() in (
            p["name"] + " " +
            (p["model_number"] or "")
        ).lower()
    ]

    return JsonResponse({
        "suggestions": matches[:8]
    })
#####################################################################################



###########################################################cart related ##################


# @login_required
# def add_to_cart(request, combo_id):
#     combo = get_object_or_404(ComboProduct, id=combo_id)

#     # Get the quantity from the form, default to 1 if not provided
#     qty = int(request.POST.get('qty', 1))

#     # Get or create cart item
#     cart_item, created = CartItem.objects.get_or_create(user=request.user, combo=combo)

#     if not created:
#         cart_item.quantity += qty  # ✅ increment by selected qty
#     else:
#         cart_item.quantity = qty  # ✅ set initial qty

#     cart_item.save()

#     messages.success(request, f"{combo.name} added to cart.")
#     return redirect('cart')


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import (
    render, redirect, get_object_or_404
)
from django.views.decorators.http import require_POST

from .models import (
    ComboProduct, Camera, CameraBullet, DVR,
    HardDisk, Cable, PowerSupply, Accessory,
    CartItem, Order, OrderItem, CustomerProfile
)


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


@login_required
@require_POST
def add_to_cart(request, product_type, product_id):

    model = PRODUCT_MODELS.get(product_type)

    if model is None:
        messages.error(request, "Invalid product.")
        return redirect("product_list")

    product = get_object_or_404(
        model, pk=product_id
    )

    try:
        qty = int(
            request.POST.get(
                "qty",
                request.POST.get("quantity", 1)
            )
        )
    except (TypeError, ValueError):
        messages.error(request, "Invalid quantity.")
        return redirect("cart")

    if qty < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect("cart")

    with transaction.atomic():

        # Serialize changes to this customer's cart.
        User = get_user_model()

        User.objects.select_for_update().get(
            pk=request.user.pk
        )

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            **{product_type: product},
            defaults={"quantity": qty}
        )

        if not created:
            cart_item.quantity += qty

        try:
            cart_item.full_clean()
        except ValidationError as exc:
            messages.error(
                request,
                "; ".join(exc.messages)
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


# @login_required
# def cart(request):
#     items = CartItem.objects.filter(user=request.user)
#     total = sum(item.subtotal() for item in items)
#     return render(request, 'home/cart.html', {'items': items, 'total': total})


# @login_required
# def remove_cart_item(request, item_id):
#     cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
#     cart_item.delete()
#     return redirect('cart')  # Redirect back to the cart page

from decimal import Decimal


@login_required
def cart(request):
    
    MINIMUM_ORDER = Decimal("5000.00")

    items = CartItem.objects.filter(
        user=request.user
    ).select_related(
        "combo", "camera", "bullet_camera",
        "dvr", "hard_disk", "cable",
        "power_supply", "accessory"
    )

    total = sum(
        (item.subtotal() for item in items),
        Decimal("0.00")
    )

    return render(request, "home/cart.html", {
        "items": items,
        "total": total
    })


@login_required
@require_POST
def remove_cart_item(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    cart_item.delete()

    messages.success(
        request,
        "Product removed from your cart."
    )

    return redirect("cart")



# @login_required
# def cart_checkout(request):
#     # Ensure address selected
#     address_id = request.session.get('selected_address_id')
#     if not address_id:
#         return redirect('select_address')

#     profile = get_object_or_404(CustomerProfile, id=address_id, user=request.user)
#     cart_items = CartItem.objects.filter(user=request.user)

#     if not cart_items.exists():
#         messages.error(request, "Your cart is empty!")
#         return redirect('product_list')

#     total = sum(item.subtotal() for item in cart_items)

#     # Razorpay order
#     client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#     payment = client.order.create({
#         'amount': int(total * 100),
#         'currency': 'INR',
#         'payment_capture': '1'
#     })

#     # Create order
#     order = Order.objects.create(
#         user=request.user,
#         profile=profile,
#         total_amount=total,
#         razorpay_order_id=payment['id']
#     )

#     # Create order items
#     for item in cart_items:
#         OrderItem.objects.create(
#             order=order,
#             combo=item.combo,
#             quantity=item.quantity,
#             price=item.combo.total_price()
#         )

#     CartItem.objects.filter(user=request.user).delete()

#     context = {
#         'order': order,
#         'profile': profile,
#         'razorpay_key': settings.RAZORPAY_KEY_ID,
#         'amount': total,
#         'payment_id': payment['id']
#     }
#     return render(request, 'home/payment.html', context)



from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

import razorpay

from .models import (
    CartItem,
    CustomerProfile,
    Order,
    OrderItem,
)

from decimal import Decimal, ROUND_HALF_UP
import razorpay

from django.conf import settings


# @login_required
# @require_POST
# def cart_checkout(request):

#     address_id = request.session.get(
#         "selected_address_id"
#     )

#     if not address_id:
#         return redirect("select_address")

#     profile = get_object_or_404(
#         CustomerProfile,
#         id=address_id,
#         user=request.user
#     )

#     cart_items = list(
#         CartItem.objects.filter(
#             user=request.user
#         ).select_related(
#             "combo", "camera", "bullet_camera",
#             "dvr", "hard_disk", "cable",
#             "power_supply", "accessory"
#         )
#     )

#     if not cart_items:
#         messages.error(
#             request,
#             "Your cart is empty!"
#         )
#         return redirect("cart")

#     # Validate quantities and stock.
#     for item in cart_items:

#         try:
#             item.full_clean()
#         except ValidationError as exc:
#             messages.error(
#                 request,
#                 f"{item.product_name}: "
#                 + "; ".join(exc.messages)
#             )
#             return redirect("cart")

#     total = sum(
#         (item.subtotal() for item in cart_items),
#         Decimal("0.00")
#     )

#     if total <= 0:
#         messages.error(
#             request,
#             "Invalid order amount."
#         )
#         return redirect("cart")

#     amount_paise = int(
#         (total * 100).quantize(
#             Decimal("1"),
#             rounding=ROUND_HALF_UP
#         )
#     )

#     client = razorpay.Client(
#         auth=(
#             settings.RAZORPAY_KEY_ID,
#             settings.RAZORPAY_KEY_SECRET
#         )
#     )

#     try:
#         payment = client.order.create({
#             "amount": amount_paise,
#             "currency": "INR",
#             "payment_capture": 1
#         })
#     except Exception:
#         messages.error(
#             request,
#             "Unable to initiate payment. Please try again."
#         )
#         return redirect("cart")

#     # Save the order and purchased item snapshots.
#     with transaction.atomic():

#         order = Order.objects.create(
#             user=request.user,
#             profile=profile,
#             total_amount=total,
#             razorpay_order_id=payment["id"],
#             payment_status="Pending"
#         )

#         for item in cart_items:

#             product_fields = {
#                 field: getattr(item, field)
#                 for field in CartItem.PRODUCT_FIELDS
#             }

#             OrderItem.objects.create(
#                 order=order,
#                 **product_fields,
#                 product_name=item.product_name,
#                 quantity=item.quantity,
#                 price=item.unit_price
#             )

#     context = {
#         "order": order,
#         "profile": profile,
#         "razorpay_key": settings.RAZORPAY_KEY_ID,
#         "amount": total,
#         "payment_id": payment["id"]
#     }

#     return render(
#         request,
#         "home/payment.html",
#         context
#     )





@login_required
@require_POST
def cart_checkout(request):

    address_id = request.session.get("selected_address_id")

    if not address_id:
        messages.error(request, "Please select a delivery address.")
        return redirect("select_address")

    profile = get_object_or_404(
        CustomerProfile,
        id=address_id,
        user=request.user
    )

    cart_items = list(
        CartItem.objects.filter(
            user=request.user
        ).select_related(
            "combo",
            "camera",
            "bullet_camera",
            "dvr",
            "hard_disk",
            "cable",
            "power_supply",
            "accessory"
        )
    )

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # Validate product selection, quantities and stock.
    for item in cart_items:
        try:
            item.full_clean()
        except ValidationError as exc:
            messages.error(
                request,
                f"{item.product_name}: {'; '.join(exc.messages)}"
            )
            return redirect("cart")

    # Calculate the current cart total on the server.
    total = sum(
        (item.subtotal() for item in cart_items),
        Decimal("0.00")
    )

    # Orders must be strictly greater than ₹5,000.
    if total <= MINIMUM_ORDER:
        messages.error(
            request,
            "Minimum order value must be more than ₹5,000. "
            "Please add more products to your cart."
        )
        return redirect("cart")

    amount_paise = int(
        (total * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    try:
        payment = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1
        })
    except Exception:
        messages.error(
            request,
            "Unable to initiate payment. Please try again."
        )
        return redirect("cart")

    # Save the pending order and item price snapshots.
    with transaction.atomic():

        order = Order.objects.create(
            user=request.user,
            profile=profile,
            total_amount=total,
            razorpay_order_id=payment["id"],
            payment_status="Pending"
        )

        for item in cart_items:

            product_fields = {
                field: getattr(item, field)
                for field in CartItem.PRODUCT_FIELDS
            }

            OrderItem.objects.create(
                order=order,
                **product_fields,
                product_name=item.product_name,
                quantity=item.quantity,
                price=item.unit_price
            )

    context = {
        "order": order,
        "profile": profile,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": total,
        "payment_id": payment["id"]
    }

    return render(
        request,
        "home/payment.html",
        context
    )
    
    
    
    
    
    

    
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





###########################################cart related end################################





import csv
from django.http import HttpResponse
from django.utils.html import strip_tags




import csv
from django.http import HttpResponse
from django.utils.html import strip_tags
from .models import ComboProduct



import csv
from django.http import HttpResponse
from django.utils.html import strip_tags
from .models import ComboProduct

import csv
from django.http import HttpResponse
from django.utils.html import strip_tags
from .models import ComboProduct



# def google_feed(request):
#     response = HttpResponse(content_type="text/csv; charset=utf-8")
#     response["Content-Disposition"] = "inline; filename=google_feed.csv"

#     writer = csv.writer(response)

#     # -------------------- HEADERS --------------------
#     writer.writerow([
#         "id",
#         "title",
#         "description",
#         "link",
#         "image_link",
#         "price",
#         "availability",
#         "condition",
#         "brand",
#         "google_product_category",
#         "mpn",
#         "product_type",
#         "included_items",
#         "identifier_exists",
#     ])

#     # -------------------- DATA ROWS --------------------
#     for combo in ComboProduct.objects.all():

#         if combo.available_stock <= 0:
#             continue  # Skip out-of-stock combos

#         availability = "in_stock"

#         # Build included items
#         components = [
#             f"Camera: {combo.camera} x {combo.camera_qty}",
#             f"DVR: {combo.dvr}",
#         ]
#         if combo.cameraBullet:
#             components.append(f"Bullet Camera: {combo.cameraBullet} x {combo.camerabullet_qty}")
#         if combo.hard_disk:
#             components.append(f"Hard Disk: {combo.hard_disk} x {combo.hard_disk_qty}")

#         components.extend([
#             f"Cable: {combo.cable} x {combo.cable_qty}",
#             f"Power Supply: {combo.power} x {combo.power_qty}",
#             f"BNC Connector: {combo.bnc_connector} x {combo.bnc_qty}",
#             f"DC Connector: {combo.dc_connector} x {combo.dc_qty}",
#             f"Installation: {combo.installation} x {combo.installation_qty}",
#         ])

#         included_items = ", ".join(components)

#         # Description
#         desc = strip_tags(combo.description or "")
#         desc = f"{desc}\n\nIncluded in Combo:\n{included_items}"

#         # Links
#         link = request.build_absolute_uri(f"/product/{combo.id}/")
#         image = request.build_absolute_uri(combo.image.url if combo.image else "/static/no-image.jpg")

#         # -------------------- WRITE ROW --------------------
#         writer.writerow([
#             f"combo-{combo.id}",          # id
#             combo.name,                   # title
#             desc[:5000],                  # description
#             link,                         # link
#             image,                        # image_link
#             f"{combo.total_price():.2f} INR",  # price
#             availability,                 # availability
#             "new",                        # condition
#             combo.brand or "Generic",     # brand
#             "6720",                        # google_product_category
#             f"SV-COMBO-{combo.id}",       # mpn
#             "CCTV Combo Kit",             # product_type
#             included_items,               # included_items
#             "FALSE",                      # identifier_exists
#         ])

#     return response


import csv

from django.http import HttpResponse
from django.utils.html import strip_tags

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


def google_feed(request):

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    response["Content-Disposition"] = (
        'inline; filename="google_feed.csv"'
    )

    writer = csv.writer(response)


    # ============================================================
    # HEADERS
    # ============================================================

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


    # ============================================================
    # COMBO PRODUCTS
    # ============================================================

    for combo in ComboProduct.objects.all():

        if combo.available_stock <= 0:
            continue

        availability = "in_stock"


        # Included items

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


        components.extend([
            f"Cable: {combo.cable} x {combo.cable_qty}",
            f"Power Supply: {combo.power} x {combo.power_qty}",
            f"BNC Connector: {combo.bnc_connector} x {combo.bnc_qty}",
            f"DC Connector: {combo.dc_connector} x {combo.dc_qty}",
            f"Installation: {combo.installation} x {combo.installation_qty}",
        ])


        included_items = ", ".join(components)


        # Description

        desc = strip_tags(
            combo.description or ""
        )

        desc = (
            f"{desc}\n\n"
            f"Included in Combo:\n"
            f"{included_items}"
        )


        # Product URL

        link = request.build_absolute_uri(
            f"/product/{combo.id}/"
        )


        # Product image

        if combo.image:

            image = request.build_absolute_uri(
                combo.image.url
            )

        else:

            image = request.build_absolute_uri(
                "/static/no-image.jpg"
            )


        # Write row

        writer.writerow([
            f"combo-{combo.id}",
            combo.name,
            desc[:5000],
            link,
            image,
            f"{combo.total_price():.2f} INR",
            availability,
            "new",
            combo.brand or "Generic",
            "6720",
            f"SV-COMBO-{combo.id}",
            "CCTV Combo Kit",
            included_items,
            "FALSE",
        ])


    # ============================================================
    # HELPER FOR INDIVIDUAL PRODUCTS
    # ============================================================

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


        # Image

        if product.image:

            image = request.build_absolute_uri(
                product.image.url
            )

        else:

            image = request.build_absolute_uri(
                "/static/no-image.jpg"
            )


        # Product link
        #
        # Currently all individual products are displayed
        # on the Accessories page.
        #
        link = request.build_absolute_uri(
            "/accessories/"
        )


        writer.writerow([
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
        ])


    # ============================================================
    # CAMERAS
    # ============================================================

    for product in Camera.objects.all():

        title = product.camera_type

        if product.model_number:
            title += f" - {product.model_number}"

        write_product(
            product=product,
            product_id=f"camera-{product.id}",
            title=title,
            description=(
                f"{title}. "
                f"CCTV security camera from Camura.in."
            ),
            product_type="CCTV Camera",
            mpn=(
                product.model_number
                or f"SV-CAMERA-{product.id}"
            ),
        )


    # ============================================================
    # BULLET CAMERAS
    # ============================================================

    for product in CameraBullet.objects.all():

        title = product.bullet_camera_type

        if product.bullet_model_number:
            title += f" - {product.bullet_model_number}"

        write_product(
            product=product,
            product_id=f"bullet-camera-{product.id}",
            title=title,
            description=(
                f"{title}. "
                f"CCTV bullet camera from Camura.in."
            ),
            product_type="CCTV Bullet Camera",
            mpn=(
                product.bullet_model_number
                or f"SV-BULLET-{product.id}"
            ),
        )


    # ============================================================
    # DVR
    # ============================================================

    for product in DVR.objects.all():

        title = product.dvr_name

        if product.model_number:
            title += f" - {product.model_number}"

        write_product(
            product=product,
            product_id=f"dvr-{product.id}",
            title=title,
            description=(
                f"{title}. "
                f"CCTV DVR from Camura.in."
            ),
            product_type="CCTV DVR",
            mpn=(
                product.model_number
                or f"SV-DVR-{product.id}"
            ),
        )


    # ============================================================
    # HARD DISK
    # ============================================================

    for product in HardDisk.objects.all():

        title = f"CCTV Hard Disk {product.size}"

        write_product(
            product=product,
            product_id=f"hard-disk-{product.id}",
            title=title,
            description=(
                f"{title} for CCTV surveillance "
                f"recording from Camura.in."
            ),
            product_type="CCTV Hard Disk",
            mpn=f"SV-HDD-{product.id}",
        )


    # ============================================================
    # CABLE
    # ============================================================

    for product in Cable.objects.all():

        title = f"CCTV Cable {product.length}"

        write_product(
            product=product,
            product_id=f"cable-{product.id}",
            title=title,
            description=(
                f"{title} for CCTV installation "
                f"from Camura.in."
            ),
            product_type="CCTV Cable",
            mpn=f"SV-CABLE-{product.id}",
        )


    # ============================================================
    # POWER SUPPLY
    # ============================================================

    for product in PowerSupply.objects.all():

        title = f"CCTV Power Supply {product.range_slug}"

        write_product(
            product=product,
            product_id=f"power-supply-{product.id}",
            title=title,
            description=(
                f"{title} for CCTV installation "
                f"from Camura.in."
            ),
            product_type="CCTV Power Supply",
            mpn=f"SV-PS-{product.id}",
        )


    # ============================================================
    # ACCESSORIES
    # ============================================================

    # for product in Accessory.objects.all():

    #     title = product.name

    #     write_product(
    #         product=product,
    #         product_id=f"accessory-{product.id}",
    #         title=title,
    #         description=(
    #             f"{title} CCTV accessory "
    #             f"from Camura.in."
    #         ),
    #         product_type="CCTV Accessory",
    #         mpn=f"SV-ACC-{product.id}",
    #     )


    return response


@login_required
def user_profile(request):
    profile = CustomerProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("customer_profile")
    else:
        form = CustomerProfileForm(instance=profile)

    edit_mode = request.GET.get("edit")  # ?edit=1 triggers edit mode

    return render(request, "home/customer_profile.html", {
        "profile": profile,
        "form": form,
        "edit_mode": edit_mode
    })











# this will remove item from cart 



# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        try:
            # Get data sent by Razorpay
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                return render(request, 'home/payment_failed.html', {'error': 'Missing payment details.'})

            # Lookup order by Razorpay order ID
            order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)

            # Verify signature to ensure payment is genuine
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                order.payment_status = 'Failed'
                order.save()
                return render(request, 'home/payment_failed.html', {'error': 'Payment signature verification failed.'})

            # Signature verified, mark order as paid
            order.payment_id = razorpay_payment_id
            order.payment_status = 'Paid'
            order.save()

            # Clear user's cart if the order was from the cart
            if order.user:
                CartItem.objects.filter(user=order.user).delete()

            # Success message and redirect
            messages.success(request, "Payment Successful! Your order has been placed.")
            return redirect('order_success')

        except Exception as e:
            print("Payment processing error:", e)
            return render(request, 'home/payment_failed.html', {'error': str(e)})

    # If GET request, redirect to home
    return redirect('home')



@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home/my_orders.html', {'orders': orders})



# @login_required
# def select_address(request):
#     addresses = CustomerProfile.objects.filter(user=request.user)
#     cart_items = CartItem.objects.filter(user=request.user)

#     from_page = request.GET.get('from')       # 'cart' or 'buy_now'
#     combo_id = request.GET.get('combo_id')

#     # ----- Determine items -----
#     if combo_id:
#         request.session['buy_now_combo_id'] = combo_id
#         combo = get_object_or_404(ComboProduct, id=combo_id)
#         total = combo.total_price()
#         items = [{'name': combo.name, 'qty': 1, 'subtotal': total}]
#     else:
#         # items = [{'name': i.combo.name, 'qty': i.quantity, 'subtotal': i.subtotal()} for i in cart_items]
#         items = [{'name': i.product_name, 'qty': i.quantity, 'price': i.unit_price, 'subtotal': i.subtotal()}
#     for i in cart_items
#     ]
#         total = sum(i['subtotal'] for i in items)

#     # ----- POST Request -----
#     if request.method == "POST":

#         # ---- Selecting an address ----
#         if 'address_id' in request.POST:
#             request.session['selected_address_id'] = request.POST.get('address_id')

#             # If Buy Now flow → redirect back to buy_now
#             if 'buy_now_combo_id' in request.session:
#                 combo_id = request.session['buy_now_combo_id']
#                 return redirect('process_buy_now', combo_id=combo_id)

#             # If Cart flow
#             if from_page == 'cart' or not combo_id:
#                 return redirect('cart_checkout')

#             return redirect('product_list')

#         # ---- Adding a new address ----
#         CustomerProfile.objects.create(
#             user=request.user,
#             full_name=request.POST['full_name'],
#             email=request.POST['email'],
#             mobile=request.POST['mobile'],
#             address=request.POST['address'],
#             city=request.POST['city'],
#             state=request.POST['state'],
#             pincode=request.POST['pincode']
#         )
#         messages.success(request, "New address added successfully!")
#         return redirect(request.path)
    
    

#     context = {
#         'addresses': addresses,
#         'items': items,
#         'total': total,
#     }
#     return render(request, 'home/select_address.html', context)










@login_required
def select_address(request):

    addresses = CustomerProfile.objects.filter(
        user=request.user
    )

    from_page = request.GET.get("from")

    # Preserve the checkout flow during POST requests.
    if request.method == "POST":
        from_page = request.POST.get("from", from_page)

    combo_id = request.GET.get("combo_id")

    if request.method == "POST":
        combo_id = request.POST.get("combo_id") or combo_id

    # Only treat a request as Buy Now when explicitly specified.
    is_buy_now = (
        from_page == "buy_now"
        and bool(combo_id)
    )

    cart_items = CartItem.objects.filter(
        user=request.user
    ).select_related(
        "combo",
        "camera",
        "bullet_camera",
        "dvr",
        "hard_disk",
        "cable",
        "power_supply",
        "accessory"
    )

    # Determine the products and total.
    if is_buy_now:

        combo = get_object_or_404(
            ComboProduct,
            pk=combo_id
        )

        total = combo.total_price()

        items = [{
            "name": combo.name,
            "qty": 1,
            "price": total,
            "subtotal": total
        }]

    else:

        items = [
            {
                "name": item.product_name,
                "qty": item.quantity,
                "price": item.unit_price,
                "subtotal": item.subtotal()
            }
            for item in cart_items
        ]

        total = sum(
            (item["subtotal"] for item in items),
            Decimal("0.00")
        )

    # Apply minimum order value to both checkout flows.
    if total <= MINIMUM_ORDER:

        messages.error(
            request,
            "Minimum order value must be more than ₹5,000."
        )

        if is_buy_now:
            return redirect(
                "product_detail",
                combo.pk
            )

        return redirect("cart")

    # Handle submitted forms.
    if request.method == "POST":

        # Select an existing address.
        if "address_id" in request.POST:

            address = get_object_or_404(
                CustomerProfile,
                pk=request.POST.get("address_id"),
                user=request.user
            )

            request.session["selected_address_id"] = address.pk

            if is_buy_now:

                request.session["buy_now_combo_id"] = combo.pk

                return redirect(
                    "process_buy_now",
                    combo_id=combo.pk
                )

            # Cart checkout must be submitted via POST.
            # Redirect to the address page to display
            # the final confirmation form.
            messages.success(
                request,
                "Address selected. Confirm your order to continue."
            )

            return redirect(
                "select_address"
            )

        # Add a new address.
        CustomerProfile.objects.create(
            user=request.user,
            full_name=request.POST["full_name"],
            email=request.POST["email"],
            mobile=request.POST["mobile"],
            address=request.POST["address"],
            city=request.POST["city"],
            state=request.POST["state"],
            pincode=request.POST["pincode"]
        )

        messages.success(
            request,
            "New address added successfully!"
        )

        # Preserve Buy Now parameters if necessary.
        if is_buy_now:
            from django.urls import reverse
            from urllib.parse import urlencode

            url = reverse("select_address")
            params = urlencode({
                "from": "buy_now",
                "combo_id": combo.pk
            })

            return redirect(f"{url}?{params}")

        return redirect("select_address")

    context = {
        "addresses": addresses,
        "items": items,
        "total": total,
        "from_page": "buy_now" if is_buy_now else "cart",
        "combo_id": combo_id if is_buy_now else "",
        "selected_address_id": request.session.get(
            "selected_address_id"
        )
    }

    return render(
        request,
        "home/select_address.html",
        context
    )
    
    
    
    
    
    
    
    
    




# Because buy_now must ONLY redirect to address selection, while
# process_buy_now must ONLY handle the payment logic.
# If you put both things in one view, it breaks the flow.

@login_required
def buy_now(request, combo_id):

    # Always force address selection first
    return redirect(f'/select_address/?from=buy_now&combo_id={combo_id}')


@login_required
def process_buy_now(request, combo_id):
    address_id = request.session.get('selected_address_id')

    if not address_id:
        return redirect(f'/select_address/?from=buy_now&combo_id={combo_id}')

    profile = get_object_or_404(CustomerProfile, id=address_id, user=request.user)
    combo = get_object_or_404(ComboProduct, id=combo_id)
    total = combo.total_price()

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({
        'amount': int(total * 100),
        'currency': 'INR',
        'payment_capture': '1'
    })

    order = Order.objects.create(
        user=request.user,
        profile=profile,
        total_amount=total,
        razorpay_order_id=payment['id']
    )

    OrderItem.objects.create(
        order=order,
        combo=combo,
        quantity=1,
        price=combo.total_price()
    )

    context = {
        'order': order,
        'profile': profile,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': total,
        'payment_id': payment['id']
    }
    return render(request, 'home/payment.html', context)







def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Send email to admin (optional)
        send_mail(
            subject=f"New Contact Message from {name}",
            message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )

        messages.success(request, "Thank you for contacting us! We’ll get back to you soon.")
        return redirect('contact')

    return render(request, 'home/contact.html')





def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')
def shipping_policy(request):
    return render(request, 'home/shipping_policy.html')
def warranty(request):
    return render(request, 'home/warranty.html')

def terms_and_conditions(request):
    return render(request, 'home/terms_and_conditions.html')

def refund_cancellation_policy(request):
    return render(request, 'home/refund_cancellation_policy.html')



@login_required
def address_list(request):
    addresses = CustomerProfile.objects.filter(user=request.user)

    # ADD NEW ADDRESS
    if request.method == "POST" and request.POST.get("form_type") == "add":
        CustomerProfile.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            mobile=request.POST.get("mobile"),
            pincode=request.POST.get("pincode"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
        )
        messages.success(request, "Address added successfully!")
        return redirect("address_list")

    # EDIT EXISTING ADDRESS
    if request.method == "POST" and request.POST.get("form_type") == "edit":
        address = get_object_or_404(CustomerProfile, id=request.POST.get("address_id"), user=request.user)

        address.full_name = request.POST.get("full_name")
        address.email = request.POST.get("email")
        address.mobile = request.POST.get("mobile")
        address.pincode = request.POST.get("pincode")
        address.address = request.POST.get("address")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.save()

        messages.success(request, "Address updated successfully!")
        return redirect("address_list")

    return render(request, "home/addresses.html", {"addresses": addresses})



@login_required
def delete_address(request, id):
    address = get_object_or_404(CustomerProfile, id=id, user=request.user)
    address.delete()
    
    messages.success(request, "Address deleted.")
    return redirect("address_list")






@login_required
def profile(request):
    profile = request.user.profile

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")

        if not full_name:
            messages.error(request, "Full name is required.")
            return redirect("profile")

        profile.full_name = full_name
        profile.email = email  # optional
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("product_list")

    return render(request, "home/profile.html", {"profile": profile})








SMS_API_KEY = config('SMS_API_KEY')
SMS_SENDER = config('SMS_SENDER')
SMS_MESSAGE = config('SMS_MESSAGE')


def send_otp(mobile):
    otp = random.randint(100000, 999999)
    url = "https://www.smsalert.co.in/api/push.json"
    data = {
        "apikey": SMS_API_KEY,
        "sender": SMS_SENDER,
        "mobileno": mobile,
        "text": SMS_MESSAGE.format(otp=otp)
    }
    requests.post(url, data=data)
    return otp




def register(request):
    stage = "mobile"

    # Get the page user originally wanted to visit
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":

        # ---------------------------------------
        # STAGE 1 → SEND OTP
        # ---------------------------------------
        if "send_otp" in request.POST:
            mobile = request.POST.get("mobile")

            otp = send_otp(mobile)

            request.session["reg_mobile"] = mobile
            request.session["reg_otp"] = otp

            request.session["user_exists"] = (
                User.objects.filter(username=mobile).exists()
            )

            # Keep next URL in session
            request.session["login_next"] = next_url

            stage = "otp"
            messages.success(request, "OTP Sent Successfully!")

        # ---------------------------------------
        # STAGE 2 → VERIFY OTP
        # ---------------------------------------
        elif "verify_otp" in request.POST:
            entered = request.POST.get("otp")
            real = str(request.session["reg_otp"])
            mobile = request.session["reg_mobile"]

            if entered == real:

                # If user exists → login
                if request.session.get("user_exists"):
                    user = User.objects.get(username=mobile)

                # Else → create new user
                else:
                    user = User.objects.create_user(
                        username=mobile,
                        password=mobile
                    )

                # Login user
                login(request, user)

                # Ensure profile exists
                profile, created = Profile.objects.get_or_create(
                    user=user
                )

                profile.mobile = mobile
                profile.save()

                # Get next URL from session
                next_url = request.session.get("login_next")

                # Clean session
                request.session.pop("reg_mobile", None)
                request.session.pop("reg_otp", None)
                request.session.pop("user_exists", None)
                request.session.pop("login_next", None)

                # ---------------------------------------
                # Redirect to original requested page
                # ---------------------------------------
                if next_url:
                    return redirect(next_url)

                # ---------------------------------------
                # Normal login → existing behavior
                # ---------------------------------------
                if profile.full_name and profile.email:
                    return redirect("product_list")
                else:
                    return redirect("profile")

            else:
                messages.error(request, "Invalid OTP")
                stage = "otp"

    return render(
        request,
        "home/register.html",
        {
            "stage": stage,
            "next_url": next_url,
        }
    )
    
    
    
    
    



@login_required
def book_service(request):
    booking_id = None

    if request.method == "POST":
        form = ServiceBookingForm(request.POST, request.FILES)

        if form.is_valid():
            # Don't save to database yet
            booking = form.save(commit=False)

            # Attach logged-in user BEFORE saving
            booking.user = request.user

            # Set amount based on service type
            prices = {
                "cctvrepair": 2000,
                "computerrepair": 1000,
            }

            booking.amount = prices.get(
                booking.service_type,
                0
            )

            # Now save everything to database
            booking.save()

            booking_id = booking.id

            return redirect(
                "booking_payment",
                booking_id=booking.id
            )

        else:
            print("FORM ERRORS:", form.errors)

    else:
        form = ServiceBookingForm()

    return render(
        request,
        "home/servicebooking.html",
        {
            "form": form,
            "booking_id": booking_id,
        }
    )





import razorpay

from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import ServiceBooking


def booking_payment(request, booking_id):

    booking = get_object_or_404(
        ServiceBooking,
        id=booking_id,
        user = request.user
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    payment = client.order.create({
        "amount": int(booking.amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    booking.razorpay_order_id = payment["id"]
    booking.save(update_fields=["razorpay_order_id"])

    return render(
        request,
        "home/booking_payment.html",
        {
            "booking": booking,
            "razorpay_order_id": payment["id"],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        }
    )
    
    
    
    
def payment_success(request, booking_id):

    booking = get_object_or_404(
        ServiceBooking,
        id=booking_id
    )

    if request.method == "POST":

        payment_id = request.POST.get(
            "razorpay_payment_id"
        )

        order_id = request.POST.get(
            "razorpay_order_id"
        )

        signature = request.POST.get(
            "razorpay_signature"
        )

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        try:

            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })

            booking.payment_status = "paid"
            booking.razorpay_payment_id = payment_id
            booking.razorpay_order_id = order_id

            booking.save()

            return render(
                request,
                "home/payment_success.html",
                {
                    "booking": booking
                }
            )

        except razorpay.errors.SignatureVerificationError:

            return render(
                request,
                "home/payment_failed.html",
                {
                    "booking": booking,
                    "error": "Payment verification failed."
                }
            )

    return redirect(
        "booking_payment",
        booking_id=booking.id
    )
    
    
    
@login_required
def my_bookings(request):

    bookings = ServiceBooking.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "home/my_bookings.html",
        {
            "bookings": bookings
        }
    )

# views.py

from django.shortcuts import get_object_or_404, redirect
from .models import ServiceBooking

def cancel_booking(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id)

    if request.method == "GET":
        booking.status = "Cancelled"
        booking.save()

    return redirect("home")
    


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from .models import ServiceBooking


def superuser_required(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(superuser_required)
def booking_list(request):
    bookings = ServiceBooking.objects.select_related("user").order_by("-created_at")

    return render(
        request,
        "home/bookings_page.html",
        {
            "bookings": bookings,
        }
    )

    
# from django.shortcuts import render
from .forms import CCTVEngineerForm



from django.conf import settings
from django.core.mail import send_mail
from .forms import CCTVEngineerForm




import requests
from django.conf import settings
from django.core.mail import send_mail
from .forms import CCTVEngineerForm

def engineer_register(request):
    message = None

    if request.method == "POST":
        form = CCTVEngineerForm(request.POST, request.FILES)
        if form.is_valid():
            engineer = form.save()

            # ------------------ EMAIL TO ADMIN ------------------
            admin_subject = "New CCTV Engineer Registration - Camura.in"
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
                [settings.ADMIN_NOTIFICATION_EMAIL],
                fail_silently=False,
            )

            # ---------------- EMAIL TO ENGINEER ------------------
            engineer_subject = "Registration Successful - Camura.in"
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
                [engineer.email],
                fail_silently=False,
            )

            # -------------------- SMS ONLY TO ENGINEER --------------------
            try:
                api_url = "https://www.smsalert.co.in/api/push.json"

                sms_message = (
                    f"Hi {engineer.full_name}, your registration as CCTV Instalation Engineer is received. Our team will contact you to verify your details. Thanks regards camura.in"
                )

                payload = {
                    "apikey": settings.SMS_API_KEY,
                    "sender": settings.SMS_SENDER,
                    "mobileno": engineer.mobile,
                    "text": sms_message,
                }

                requests.post(api_url, data=payload, timeout=10)

            except Exception as e:
                print("SMS Error:", e)

            # ------------------------------------------------------

            message = "Registration successful! Confirmation email and SMS have been sent."
            form = CCTVEngineerForm()
    else:
        form = CCTVEngineerForm()

    return render(request, 'home/engineer_register.html', {
        'form': form,
        'message': message
    })
