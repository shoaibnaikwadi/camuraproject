from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    Product,
    ComboComponent,
    CartItem,
    Order,
    OrderItem,
    CustomerProfile,
    Profile,
    ServiceBooking,
    CCTVEngineer,
    JobOpening,
    ProductReview,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


class ComboComponentInline(admin.TabularInline):
    model = ComboComponent
    fk_name = "combo"
    extra = 1
    autocomplete_fields = ("component",)


# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = (
#         "thumbnail",
#         "name",
#         "sku",
#         "product_type",
#         "brand",
#         "camera_type",
#         "camera_quantity",
#         "category",
#         "price",
#         "stock",
#         "available_stock",
#         "is_active",
#     )
#     list_filter = ("product_type", "brand", "camera_type", "category", "is_active")
#     search_fields = ("name", "sku", "description")
#     list_editable = ("price", "stock", "is_active")
#     prepopulated_fields = {"slug": ("name",)}
#     readonly_fields = ("thumbnail", "available_stock")
#     inlines = (ComboComponentInline,)

#     fieldsets = (
#         (
#             "Product Information",
#             {
#                 "fields": (
#                     "name",
#                     "slug",
#                     "sku",
#                     "product_type",
#                     "category",
#                     "description",
#                     "main_image",
#                 )
#             },
#         ),
#         (
#             "Pricing and Inventory",
#             {
#                 "fields": (
#                     "price",
#                     "stock",
#                     "available_stock",
#                     "is_active",
#                 )
#             },
#         ),
#         ("Image Preview", {"fields": ("thumbnail",)}),
#     )

#     @admin.display(description="Image")
#     def thumbnail(self, obj):
#         if obj and obj.main_image:
#             return format_html(
#                 '<img src="{}" width="55" height="55" '
#                 'style="object-fit:cover;border-radius:6px;" />',
#                 obj.main_image.url,
#             )
#         return "-"






@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "thumbnail",
        "name",
        "sku",
        "product_type",
        "brand",
        "camera_type",
        "camera_quantity",
        "category",
        "price",
        "available_stock",
        "is_active",
    )

    list_filter = (
        "product_type",
        "brand",
        "camera_type",
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "sku",
        "brand",
        "description",
    )

    list_editable = (
        "brand",
        "camera_type",
        "camera_quantity",
        "price",
        "is_active",
    )

    prepopulated_fields = {"slug": ("name",)}

    readonly_fields = ("thumbnail", "available_stock")

    inlines = (ComboComponentInline,)

    fieldsets = (
        (
            "Product Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "sku",
                    "product_type",
                    "category",
                    "description",
                    "main_image",
                )
            },
        ),
        (
            "Brand and Camera Filters",
            {
                "fields": (
                    "brand",
                    "camera_type",
                    "camera_quantity",
                )
            },
        ),
        (
            "Pricing and Inventory",
            {
                "fields": (
                    "price",
                    "stock",
                    "available_stock",
                    "is_active",
                )
            },
        ),
        ("Image Preview", {"fields": ("thumbnail",)}),
    )

    @admin.display(description="Image")
    def thumbnail(self, obj):
        if obj and obj.main_image:
            return format_html(
                '<img src="{}" width="55" height="55" '
                'style="object-fit:cover;border-radius:6px;" />',
                obj.main_image.url,
            )
        return "-"
    
    
    
    
    
    
    
@admin.register(ComboComponent)
class ComboComponentAdmin(admin.ModelAdmin):
    list_display = ("combo", "component", "quantity")
    list_filter = ("combo__category",)
    search_fields = (
        "combo__name",
        "combo__sku",
        "component__name",
        "component__sku",
    )
    autocomplete_fields = ("combo", "component")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__username", "comment")
    autocomplete_fields = ("product", "user")
    readonly_fields = ("created_at",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "quantity",
        "available_stock",
        "subtotal_display",
    )
    list_filter = ("product__product_type",)
    search_fields = (
        "user__username",
        "product__name",
        "product__sku",
    )
    autocomplete_fields = ("user", "product")
    readonly_fields = ("available_stock", "subtotal_display")

    @admin.display(description="Available stock")
    def available_stock(self, obj):
        if obj and obj.product_id:
            return obj.product.available_stock
        return "-"

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        if obj and obj.pk:
            return f"₹{obj.subtotal():,.2f}"
        return "-"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = (
        "product",
        "product_name",
        "product_sku",
        "quantity",
        "price",
        "subtotal_display",
    )
    readonly_fields = ("subtotal_display",)
    autocomplete_fields = ("product",)

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        if obj and obj.pk:
            return f"₹{obj.subtotal():,.2f}"
        return "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "profile",
        "total_amount",
        "payment_method",
        "payment_status",
        "order_status",
        "created_at",
    )
    list_filter = (
        "payment_method",
        "payment_status",
        "order_status",
        "created_at",
    )
    search_fields = (
        "user__username",
        "profile__full_name",
        "profile__mobile",
        "razorpay_order_id",
        "payment_id",
    )
    readonly_fields = (
        "razorpay_order_id",
        "payment_id",
        "created_at",
    )
    inlines = (OrderItemInline,)
    ordering = ("-created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product_name",
        "product_sku",
        "quantity",
        "price",
        "subtotal_display",
    )
    search_fields = (
        "product_name",
        "product_sku",
        "order__id",
    )
    list_filter = (
        "order__payment_status",
        "order__order_status",
    )
    readonly_fields = ("subtotal_display",)
    autocomplete_fields = ("product", "order")

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        if obj and obj.pk:
            return f"₹{obj.subtotal():,.2f}"
        return "-"


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "mobile",
        "city",
        "state",
        "created_at",
    )
    search_fields = (
        "full_name",
        "email",
        "mobile",
        "city",
        "state",
        "pincode",
    )
    list_filter = ("state", "city")
    readonly_fields = ("created_at",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "mobile", "email", "user")
    search_fields = (
        "full_name",
        "mobile",
        "email",
        "user__username",
    )
    list_filter = ("email",)
    autocomplete_fields = ("user",)


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "mobile",
        "service_type",
        "amount",
        "payment_status",
        "status",
        "preferred_date",
        "preferred_time",
        "created_at",
    )
    list_editable = ("status",)
    list_filter = (
        "service_type",
        "payment_status",
        "status",
        "preferred_date",
        "created_at",
    )
    search_fields = (
        "name",
        "mobile",
        "email",
        "problem_description",
        "razorpay_order_id",
        "razorpay_payment_id",
    )
    readonly_fields = (
        "created_at",
        "razorpay_order_id",
        "razorpay_payment_id",
    )
    ordering = ("-created_at",)


@admin.register(CCTVEngineer)
class CCTVEngineerAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "mobile",
        "email",
        "city",
        "experience",
        "certified",
        "colored_status",
        "date_registered",
    )
    list_filter = ("status", "certified", "city")
    search_fields = ("full_name", "mobile", "email", "city")
    readonly_fields = (
        "date_registered",
        "preview_government_id",
    )
    fieldsets = (
        (
            "Personal Details",
            {
                "fields": (
                    "full_name",
                    "mobile",
                    "email",
                    "city",
                    "address",
                    "experience",
                    "certified",
                    "status",
                )
            },
        ),
        (
            "Government ID",
            {
                "fields": (
                    "government_id",
                    "preview_government_id",
                )
            },
        ),
        ("System Info", {"fields": ("date_registered",)}),
    )

    @admin.display(description="Status")
    def colored_status(self, obj):
        color = {
            "pending": "orange",
            "verified": "green",
            "hold": "red",
        }.get(obj.status, "black")

        return format_html(
            '<span style="color:{};font-weight:bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="Preview ID")
    def preview_government_id(self, obj):
        if (
            obj
            and obj.government_id
            and obj.government_id.name.lower().endswith(
                (".jpg", ".jpeg", ".png")
            )
        ):
            return format_html(
                '<img src="{}" width="200" '
                'style="height:auto;border-radius:6px;" />',
                obj.government_id.url,
            )
        return "No preview available"


@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "location",
        "job_type",
        "vacancies",
        "last_date",
        "is_active",
    )
    list_filter = ("job_type", "is_active", "location")
    search_fields = ("title", "location", "qualification")
    list_editable = ("is_active",)
    ordering = ("-created_at",)