from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
###########################################
    path('productlist/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),


    # path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    # path('buy-now/<int:pk>/', views.buy_now, name='buy_now'),
    # Cart checkout
    # path('checkout/', views.checkout, name='checkout'),

    # Buy Now checkout (single product)
    # path('buy-now/<int:combo_id>/', views.checkout, name='buy_now'),

    # Cart checkout
    path('checkout/', views.cart_checkout, name='cart_checkout'),

    # Buy Now checkout
    path('buy-now/<int:combo_id>/', views.buy_now, name='buy_now'),
    path('process-buy-now/<int:combo_id>/', views.process_buy_now, name='process_buy_now'),


    # path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),

    # Staff manage dashboard
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    # cash on delivery url
    path('cod-payment/', views.cod_payment, name='cod_payment'),
    

    # Camera CRUD (example)
    path('staff/camera/add/', views.add_camera, name='add_camera'),
    path('staff/camera/<int:pk>/edit/', views.edit_camera, name='edit_camera'),
    path('staff/camera/<int:pk>/delete/', views.delete_camera, name='delete_camera'),

    # Combo CRUD
    path('staff/combo/add/', views.add_combo, name='add_combo'),
    path('staff/combo/<int:pk>/edit/', views.edit_combo, name='edit_combo'),
    path('staff/combo/<int:pk>/delete/', views.delete_combo, name='delete_combo'),

    # (Add other CRUD routes for DVR, Cable, Power, Accessory, Install similarly)


    #########################################################
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:combo_id>/', views.add_to_cart, name='add_to_cart'),

    path('customer-profile/', views.customer_profile, name='customer_profile'),
    path('myorders/', views.my_orders, name='my_orders'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('order-success/', TemplateView.as_view(template_name='home/order_success.html'), name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    # path('checkout/<int:combo_id>/', views.checkout, name='checkout_with_combo'),
    path('select_address/', views.select_address, name='select_address'),

    # path('select-address/', views.select_address, name='select_address'),
    path('about/', TemplateView.as_view(template_name='home/about.html'), name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('refund-cancellation-policy/', views.refund_cancellation_policy, name='refund_cancellation_policy'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)