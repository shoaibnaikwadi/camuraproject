
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views
from django.contrib.sitemaps.views import sitemap

from home.sitemaps import (
    StaticViewSitemap,
    ProductSitemap,
    JobOpeningSitemap,
)
from blog.sitemaps import BlogSitemap


sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
    "jobs": JobOpeningSitemap,
    "blog": BlogSitemap,

}


urlpatterns = [

    # =========================================================
    # HOME & AUTHENTICATION
    # =========================================================

    path("", views.home, name="home"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="home/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="home"
        ),
        name="logout",
    ),

    path(
        "register/",
        views.register,
        name="register",
    ),

    # Keep old registration URL if still used anywhere
    path(
        "registerold/",
        views.registerold,
        name="registerold",
    ),


    # =========================================================
    # PRODUCTS
    # =========================================================

    path(
        "productlist/",
        views.product_list,
        name="product_list",
    ),

    path(
        "product/<int:pk>/",
        views.product_detail,
        name="product_detail",
    ),

    path(
        "accessories/",
        views.accessories,
        name="accessories",
    ),

    path(
        "accessories/suggestions/",
        views.accessory_suggestions,
        name="accessory_suggestions",
    ),


    # =========================================================
    # CART
    # =========================================================

    path(
        "add-to-cart/<str:product_type>/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart",
    ),

    path(
        "cart/",
        views.cart,
        name="cart",
    ),

    path(
        "remove-cart-item/<int:item_id>/",
        views.remove_cart_item,
        name="remove_cart_item",
    ),

    path(
        "clear-cart/",
        views.clear_cart,
        name="clear_cart",
    ),


    # =========================================================
    # CHECKOUT & ORDERS
    # =========================================================

    path(
        "checkout/",
        views.cart_checkout,
        name="checkout_page",
    ),

    # Keep this only if old templates/links still use cart_checkout
    path(
        "cart-checkout/",
        views.cart_checkout,
        name="cart_checkout",
    ),

    # Buy Now
    path(
        "buy-now/<int:combo_id>/",
        views.buy_now,
        name="buy_now",
    ),

    path(
        "process-buy-now/<int:combo_id>/",
        views.process_buy_now,
        name="process_buy_now",
    ),

    # COD
    path(
        "cod-payment/",
        views.cod_payment,
        name="cod_payment",
    ),

    # Razorpay / online payment success
    path(
        "payment-success/",
        views.payment_success,
        name="payment_success",
    ),

    # Order success page
    # IMPORTANT:
    # If your template/view needs order_id, use:
    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success",
    ),

    path(
        "my-orders/",
        views.my_orders,
        name="my_orders",
    ),


    # =========================================================
    # USER PROFILE & ADDRESSES
    # =========================================================

    path(
        "profile/",
        views.profile,
        name="profile",
    ),

    path(
        "addresses/",
        views.address_list,
        name="address_list",
    ),

    path(
        "select-address/",
        views.select_address,
        name="select_address",
    ),

    path(
        "address/delete/<int:id>/",
        views.delete_address,
        name="delete_address",
    ),


    # =========================================================
    # STATIC INFORMATION PAGES
    # =========================================================

    path(
        "about/",
        TemplateView.as_view(
            template_name="home/about.html"
        ),
        name="about",
    ),

    path(
        "contact/",
        views.contact_view,
        name="contact",
    ),

    path(
        "privacy-policy/",
        views.privacy_policy,
        name="privacy_policy",
    ),

    path(
        "shipping-policy/",
        views.shipping_policy,
        name="shipping_policy",
    ),

    path(
        "warranty/",
        views.warranty,
        name="warranty",
    ),

    path(
        "terms-and-conditions/",
        views.terms_and_conditions,
        name="terms_and_conditions",
    ),

    path(
        "refund-cancellation-policy/",
        views.refund_cancellation_policy,
        name="refund_cancellation_policy",
    ),

    path(
        "google-feed/",
        views.google_feed,
        name="google_feed",
    ),


    # =========================================================
    # SERVICE BOOKING
    # =========================================================

    path(
        "engineer/register/",
        views.engineer_register,
        name="engineer_register",
    ),

    path(
        "book-service/",
        views.book_service,
        name="book_service",
    ),

    path(
        "booking-payment/<int:booking_id>/",
        views.booking_payment,
        name="booking_payment",
    ),

    path(
        "booking-payment-success/<int:booking_id>/",
        views.booking_payment_success,
        name="booking_payment_success",
    ),  

    path(
        "my-bookings/",
        views.my_bookings,
        name="my_bookings",
    ),

    path(
        "booking/<int:booking_id>/cancel/",
        views.cancel_booking,
        name="cancel_booking",
    ),

    path(
        "bookings/",
        views.booking_list,
        name="booking_list",
    ),


    # =========================================================
    # CKEDITOR
    # =========================================================

    path(
        "ckeditor5/",
        include("django_ckeditor_5.urls"),
    ),
    
    
    path(
            "admin-orders/",
            views.admin_orders,
            name="admin_orders",
        ),
    
    path(
        "admin-orders/<int:order_id>/status/",
        views.update_order_status,
        name="update_order_status",
    ),
    
    path(
        "registered-engineers/",
        views.registered_engineers,
        name="registered_engineers",
    ),

    path(
        "registered-engineers/<int:engineer_id>/status/",
        views.update_engineer_status,
        name="update_engineer_status",
    ),
    
    
    path("careers/", views.careers, name="careers"),
    
    path("careers/<int:job_id>/", views.job_detail, name="job_detail"),
    
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django_sitemap",),
]


# =============================================================
# MEDIA FILES - DEVELOPMENT ONLY
# =============================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )




    