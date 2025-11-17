from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import razorpay
from django.conf import settings
from .models import Order, OrderItem, CartItem, ComboProduct, CustomerProfile

from .forms import CustomerProfileForm


from .models import Order, OrderItem, CartItem, CustomerProfile, ComboProduct
# @login_required
def home(request):
    return render(request, 'home/index.html')






def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'home/register.html', {'form': form})

# @login_required
# def dashboard(request):
#     return render(request, 'dashboard.html')


# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Camera, DVR, Cable, PowerSupply, Accessory, InstallationCharge, ComboProduct
from .forms import (CameraForm, DVRForm, CableForm, PowerSupplyForm,
                    AccessoryForm, InstallationForm, ComboForm)

# PUBLIC SHOP VIEWS

def product_list(request):
    combos = ComboProduct.objects.all()
    return render(request, 'home/product_list.html', {'combos': combos})

def product_detail(request, pk):
    combo = get_object_or_404(ComboProduct, pk=pk)
    return render(request, 'home/product_detail.html', {'combo': combo})

def clear_cart(request):
    request.session['cart'] = {}
    return redirect('view_cart')




from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Order

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

# Repeat for DVR, Cable, PowerSupply, Accessory, InstallationCharge, ComboProduct
# For brevity include Combo add/edit/delete below:

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




#####################################################################################
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ComboProduct, CartItem, Order

@login_required
def add_to_cart(request, combo_id):
    combo = get_object_or_404(ComboProduct, id=combo_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, combo=combo)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"{combo.name} added to cart.")
    return redirect('cart')

@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in items)
    return render(request, 'home/cart.html', {'items': items, 'total': total})




# @login_required
# def customer_profile(request):
#     try:
#         profile = CustomerProfile.objects.get(user=request.user)
#     except CustomerProfile.DoesNotExist:
#         profile = None

#     if request.method == 'POST':
#         form = CustomerProfileForm(request.POST, instance=profile)
#         if form.is_valid():
#             profile = form.save(commit=False)
#             profile.user = request.user
#             profile.save()
#             messages.success(request, "Profile updated successfully!")
#             return redirect('customer_profile')
#     else:
#         form = CustomerProfileForm(instance=profile)

#     return render(request, 'home/customer_profile.html', {'form': form})





@login_required
def user_profile(request):
    profile = CustomerProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("user_profile")
    else:
        form = CustomerProfileForm(instance=profile)

    edit_mode = request.GET.get("edit")  # ?edit=1 triggers edit mode

    return render(request, "home/customer_profile.html", {
        "profile": profile,
        "form": form,
        "edit_mode": edit_mode
    })





from .models import CartItem, Order, OrderItem, CustomerProfile, ComboProduct

# -------------------------------
# Cart Checkout View
# -------------------------------
# @login_required
# def cart_checkout(request):
#     profile, created = CustomerProfile.objects.get_or_create(user=request.user)
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

#     # Create Order
#     order = Order.objects.create(
#         user=request.user,
#         profile=profile,
#         total_amount=total,
#         razorpay_order_id=payment['id']
#     )

#     # Create Order Items
#     for item in cart_items:
#         OrderItem.objects.create(
#             order=order,
#             combo=item.combo,
#             quantity=item.quantity,
#             price=item.combo.total_price()
#         )

#     # Clear cart
#     CartItem.objects.filter(user=request.user).delete()

#     context = {
#         'order': order,
#         'profile': profile,
#         'razorpay_key': settings.RAZORPAY_KEY_ID,
#         'amount': total,
#         'payment_id': payment['id']
#     }
#     return render(request, 'home/payment.html', context)


# # -------------------------------
# # Buy Now View
# # -------------------------------
# @login_required
# def buy_now(request, combo_id):
#     profile, created = CustomerProfile.objects.get_or_create(user=request.user)
#     combo = get_object_or_404(ComboProduct, id=combo_id)
#     total = combo.total_price()

#     # Razorpay order
#     client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#     payment = client.order.create({
#         'amount': int(total * 100),
#         'currency': 'INR',
#         'payment_capture': '1'
#     })

#     # Create Order
#     order = Order.objects.create(
#         user=request.user,
#         profile=profile,
#         total_amount=total,
#         razorpay_order_id=payment['id']
#     )

#     # Create single OrderItem
#     OrderItem.objects.create(
#         order=order,
#         combo=combo,
#         quantity=1,
#         price=combo.total_price()
#     )

#     context = {
#         'order': order,
#         'profile': profile,
#         'razorpay_key': settings.RAZORPAY_KEY_ID,
#         'amount': total,
#         'payment_id': payment['id']
#     }
#     return render(request, 'home/payment.html', context)




from django.views.decorators.csrf import csrf_exempt





# this will remove item from cart 
@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')  # Redirect back to the cart page



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

#     if request.method == "POST":
#         if 'address_id' in request.POST:
#             # Save the selected address in session
#             request.session['selected_address_id'] = request.POST.get('address_id')
#             next_step = request.POST.get('next', 'cart_checkout')
#             return redirect(next_step)

#         # Add a new address
#         CustomerProfile.objects.create(
#             user=request.user,
#             full_name=request.POST['full_name'],
#             email=request.POST['email'],
#             mobile=request.POST['mobile'],
#             address=request.POST['address'],
#             city=request.POST['city'],
#             state=request.POST['state'],
#             pincode=request.POST['pincode'],
#             is_default=False
#         )
#         messages.success(request, "New address added successfully!")
#         return redirect('select_address')

#     context = {
#         'addresses': addresses,
#     }
#     return render(request, 'home/select_address.html', context)



# @login_required
# def select_address(request):
#     addresses = CustomerProfile.objects.filter(user=request.user)
#     cart_items = CartItem.objects.filter(user=request.user)

#     # If coming from buy_now, store combo_id in session
#     combo_id = request.GET.get('combo_id')
#     if combo_id:
#         request.session['buy_now_combo_id'] = combo_id
#         combo = get_object_or_404(ComboProduct, id=combo_id)
#         total = combo.total_price()
#         items = [{'name': combo.name, 'qty': 1, 'subtotal': total}]
#     else:
#         items = [{'name': i.combo.name, 'qty': i.quantity, 'subtotal': i.subtotal()} for i in cart_items]
#         total = sum(i['subtotal'] for i in items)

#     if request.method == "POST":
#         # If selecting an address
#         if 'address_id' in request.POST:
#             request.session['selected_address_id'] = request.POST.get('address_id')

#             # Redirect to correct checkout flow
#             if 'buy_now_combo_id' in request.session:
#                 return redirect('buy_now', combo_id=request.session['buy_now_combo_id'])
#             else:
#                 return redirect('cart_checkout')

#         # Add a new address
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
#         return redirect('select_address')

#     context = {
#         'addresses': addresses,
#         'items': items,
#         'total': total,
#     }
#     return render(request, 'home/select_address.html', context)






# @login_required
# def select_address(request):
#     addresses = CustomerProfile.objects.filter(user=request.user)
#     cart_items = CartItem.objects.filter(user=request.user)
#     from_page = request.GET.get('from')  # 'cart' or 'buy_now'
#     combo_id = request.GET.get('combo_id')

#     # Determine order items
#     if combo_id:
#         request.session['buy_now_combo_id'] = combo_id
#         combo = get_object_or_404(ComboProduct, id=combo_id)
#         total = combo.total_price()
#         items = [{'name': combo.name, 'qty': 1, 'subtotal': total}]
#     else:
#         items = [{'name': i.combo.name, 'qty': i.quantity, 'subtotal': i.subtotal()} for i in cart_items]
#         total = sum(i['subtotal'] for i in items)

#     if request.method == "POST":
#         # Select address
#         if 'address_id' in request.POST:
#             request.session['selected_address_id'] = request.POST.get('address_id')

#             # Redirect to checkout page based on source
#             if 'buy_now_combo_id' in request.session:
#                 return redirect('buy_now', combo_id=request.session['buy_now_combo_id'])
#             elif from_page == 'cart' or not combo_id:
#                 return redirect('cart_checkout')
#             else:
#                 return redirect('product_list')

#         # Add new address
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
    addresses = CustomerProfile.objects.filter(user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)

    from_page = request.GET.get('from')       # 'cart' or 'buy_now'
    combo_id = request.GET.get('combo_id')

    # ----- Determine items -----
    if combo_id:
        request.session['buy_now_combo_id'] = combo_id
        combo = get_object_or_404(ComboProduct, id=combo_id)
        total = combo.total_price()
        items = [{'name': combo.name, 'qty': 1, 'subtotal': total}]
    else:
        items = [{'name': i.combo.name, 'qty': i.quantity, 'subtotal': i.subtotal()} for i in cart_items]
        total = sum(i['subtotal'] for i in items)

    # ----- POST Request -----
    if request.method == "POST":

        # ---- Selecting an address ----
        if 'address_id' in request.POST:
            request.session['selected_address_id'] = request.POST.get('address_id')

            # If Buy Now flow → redirect back to buy_now
            if 'buy_now_combo_id' in request.session:
                combo_id = request.session['buy_now_combo_id']
                return redirect('process_buy_now', combo_id=combo_id)

            # If Cart flow
            if from_page == 'cart' or not combo_id:
                return redirect('cart_checkout')

            return redirect('product_list')

        # ---- Adding a new address ----
        CustomerProfile.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            email=request.POST['email'],
            mobile=request.POST['mobile'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            pincode=request.POST['pincode']
        )
        messages.success(request, "New address added successfully!")
        return redirect(request.path)

    context = {
        'addresses': addresses,
        'items': items,
        'total': total,
    }
    return render(request, 'home/select_address.html', context)








@login_required
def cart_checkout(request):
    # Ensure address selected
    address_id = request.session.get('selected_address_id')
    if not address_id:
        return redirect('select_address')

    profile = get_object_or_404(CustomerProfile, id=address_id, user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('product_list')

    total = sum(item.subtotal() for item in cart_items)

    # Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({
        'amount': int(total * 100),
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Create order
    order = Order.objects.create(
        user=request.user,
        profile=profile,
        total_amount=total,
        razorpay_order_id=payment['id']
    )

    # Create order items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            combo=item.combo,
            quantity=item.quantity,
            price=item.combo.total_price()
        )

    CartItem.objects.filter(user=request.user).delete()

    context = {
        'order': order,
        'profile': profile,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': total,
        'payment_id': payment['id']
    }
    return render(request, 'home/payment.html', context)


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





# @login_required
# def buy_now(request, combo_id):
#     address_id = request.session.get('selected_address_id')
#     if not address_id:
#         return redirect('select_address')

#     profile = get_object_or_404(CustomerProfile, id=address_id, user=request.user)
#     combo = get_object_or_404(ComboProduct, id=combo_id)
#     total = combo.total_price()

#     client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#     payment = client.order.create({
#         'amount': int(total * 100),
#         'currency': 'INR',
#         'payment_capture': '1'
#     })

#     order = Order.objects.create(
#         user=request.user,
#         profile=profile,
#         total_amount=total,
#         razorpay_order_id=payment['id']
#     )

#     OrderItem.objects.create(
#         order=order,
#         combo=combo,
#         quantity=1,
#         price=combo.total_price()
#     )

#     context = {
#         'order': order,
#         'profile': profile,
#         'razorpay_key': settings.RAZORPAY_KEY_ID,
#         'amount': total,
#         'payment_id': payment['id']
#     }
#     return render(request, 'home/payment.html', context)


from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

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

def terms_and_conditions(request):
    return render(request, 'home/terms_and_conditions.html')

def refund_cancellation_policy(request):
    return render(request, 'home/refund_cancellation_policy.html')

