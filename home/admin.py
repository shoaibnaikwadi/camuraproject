# shop/admin.py
from django.contrib import admin
from django.utils.html import format_html  # <-- ADD THIS
from .models import (
    Camera,
    DVR,
    Cable,
    PowerSupply,
    Accessory,
    InstallationCharge,
    ComboProduct,
    CartItem, Order, CustomerProfile, HardDisk
)

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('camera_type', 'price')
    list_filter = ('camera_type',)
    search_fields = ('camera_type',)


@admin.register(DVR)
class DVRAdmin(admin.ModelAdmin):
    list_display = ('resolution', 'channels', 'price')
    list_filter = ('resolution', 'channels')
    search_fields = ('resolution', 'channels')


@admin.register(HardDisk)
class HardDiskAdmin(admin.ModelAdmin):
    list_display = ("size", "price")


@admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
    list_display = ('length', 'price')
    list_filter = ('length',)
    search_fields = ('length',)


@admin.register(PowerSupply)
class PowerSupplyAdmin(admin.ModelAdmin):
    list_display = ('range_slug', 'price')
    list_filter = ('range_slug',)
    search_fields = ('range_slug',)


@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


@admin.register(InstallationCharge)
class InstallationChargeAdmin(admin.ModelAdmin):
    list_display = ('description', 'price')
    search_fields = ('description',)







@admin.register(ComboProduct)
class ComboProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail',
        'name',
        'camera', 'camera_qty',
        'dvr',
        'hard_disk', 'hard_disk_qty',
        'cable', 'cable_qty',
        'power', 'power_qty',
        'bnc_connector', 'bnc_qty',
        'dc_connector', 'dc_qty',
        'installation', 'installation_qty',
        'total_price',
        'created_at',
    )

    fields = (
        'name',
        'camera', 'camera_qty',
        'dvr',
        'hard_disk', 'hard_disk_qty',
        'cable', 'cable_qty',
        'power', 'power_qty',
        'bnc_connector', 'bnc_qty',
        'dc_connector', 'dc_qty',
        'installation', 'installation_qty',
        'description',
        'image',
    )

    search_fields = ('name', 'description')
    list_filter = ('camera', 'dvr', 'power', 'installation')

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:4px;" />', obj.image.url)
        return "-"
    thumbnail.short_description = "Image"




# @admin.register(ComboProduct)
# class ComboProductAdmin(admin.ModelAdmin):
#     list_display = (
#         'thumbnail',  # <-- Add thumbnail firs
#         'name',
#         'camera',
#         'camera_qty',
#         'dvr',
#         'cable',
#         'power',
#         'bnc_connector',
#         'dc_connector',
#         'installation',
#         'total_price',
#         'created_at',
#     )
#     search_fields = ('name', 'description')
#     list_filter = ('camera', 'dvr', 'power', 'installation')

#     fields = (
#         'name',
#         'camera',
#         'camera_qty',
#         'dvr',
#         'cable',
#         'power',
#         'bnc_connector',
#         'dc_connector',
#         'installation',
#         'description',
#         'image',  # file upload
#     )

#     def thumbnail(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:4px;" />', obj.image.url)
#         return "-"
#     thumbnail.short_description = "Image"





@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'combo', 'quantity', 'subtotal_display')
    list_filter = ('user',)
    search_fields = ('user__username', 'combo__name')

    def subtotal_display(self, obj):
        return f"₹{obj.subtotal():,.2f}"
    subtotal_display.short_description = "Subtotal"




@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'mobile', 'city', 'state', 'created_at')
    search_fields = ('full_name', 'email', 'mobile', 'city', 'state')
    list_filter = ('state', 'city')
    readonly_fields = ('created_at',)


from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No extra blank rows

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'profile', 'total_amount', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('user__username', 'profile__full_name', 'razorpay_order_id', 'payment_id')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)  # Optional: You can register separately if needed





from django.contrib import admin
from .models import ServiceBooking

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "mobile",
        "service_type",
        "preferred_date",
        "preferred_time",
        "status",
        "created_at",
    )

    list_filter = (
        "service_type",
        "status",
        "preferred_date",
        "created_at",
    )

    search_fields = (
        "name",
        "mobile",
        "problem_description",
    )

    list_editable = (
        "status",
    )

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)
