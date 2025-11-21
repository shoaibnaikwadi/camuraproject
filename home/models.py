# shop/models.py
from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
# from .models import CustomerProfile, Combo


# CAMERA MASTER
class Camera(models.Model):
    CAMERA_TYPES = [
        ('2mp', '2MP'),
        ('2mp_color', '2MP Color'),
        ('5mp', '5MP'),
        ('5mp_color', '5MP Color'),
    ]
    camera_type = models.CharField(max_length=30, choices=CAMERA_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_camera_type_display()} (₹{self.price})"


# DVR MASTER
class DVR(models.Model):
    CHANNEL_CHOICES = [
        ('4ch', '4 CH'),
        ('8ch', '8 CH'),
        ('16ch', '16 CH'),
        ('32ch', '32 CH'),
    ]
    RES_CHOICES = [
        ('2mp', '2MP'),
        ('5mp', '5MP'),
    ]
    channels = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    resolution = models.CharField(max_length=10, choices=RES_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_resolution_display()} {self.get_channels_display()} DVR (₹{self.price})"


# class HardDisk(models.Model):
#     brand = models.CharField(max_length=100)
#     capacity = models.CharField(max_length=50)   # Example: "500GB", "1TB"
#     model_number = models.CharField(max_length=100)

#     def __str__(self):
#         return f"{self.brand} {self.capacity} ({self.model_number})"


class HardDisk(models.Model):
    size = models.CharField(max_length=50)   # e.g., 1TB, 2TB
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.size} HDD (₹{self.price})"

# CABLE MASTER
class Cable(models.Model):
    LENGTH_CHOICES = [('90m', '90 Meter'), ('180m', '180 Meter')]
    length = models.CharField(max_length=10, choices=LENGTH_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_length_display()} (₹{self.price})"


# POWER SUPPLY MASTER
class PowerSupply(models.Model):
    RANGE_CHOICES = [
        ('1-4', '1–4 Cameras'),
        ('4-8', '4–8 Cameras'),
        ('8-16', '8–16 Cameras'),
        ('16-32', '16–32 Cameras'),
    ]
    range_slug = models.CharField(max_length=10, choices=RANGE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_range_slug_display()} (₹{self.price})"


# ACCESSORY MASTER (BNC, DC, etc.)
class Accessory(models.Model):
    name = models.CharField(max_length=100)  # e.g., "BNC Connector", "DC Connector"
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} (₹{self.price})"


# INSTALLATION CHARGES MASTER
class InstallationCharge(models.Model):
    description = models.CharField(max_length=200, default="Installation")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} (₹{self.price})"






# COMBO / PRODUCT (built from masters)
class ComboProduct(models.Model):
    name = models.CharField(max_length=150)

    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    camera_qty = models.PositiveIntegerField(default=2)

    dvr = models.ForeignKey(DVR, on_delete=models.CASCADE)

    # hard_disk = models.ForeignKey(HardDisk, on_delete=models.SET_NULL, null=True, blank=True)
    # hard_disk_qty = models.PositiveIntegerField(default=1)

    hard_disk = models.ForeignKey(HardDisk, on_delete=models.CASCADE, null=True, blank=True)
    hard_disk_qty = models.PositiveIntegerField(default=1)

    cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
    cable_qty = models.PositiveIntegerField(default=1)   # NEW

    power = models.ForeignKey(PowerSupply, on_delete=models.CASCADE)
    power_qty = models.PositiveIntegerField(default=1)   # NEW

    bnc_connector = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='bnc_in_combo')
    bnc_qty = models.PositiveIntegerField(default=2)     # NEW

    dc_connector = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='dc_in_combo')
    dc_qty = models.PositiveIntegerField(default=2)      # NEW

    installation = models.ForeignKey(InstallationCharge, on_delete=models.CASCADE)
    installation_qty = models.PositiveIntegerField(default=1)  # NEW

    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        total = Decimal('0.00')

        total += (self.camera.price * Decimal(self.camera_qty))
        total += self.dvr.price
        total += (self.cable.price * Decimal(self.cable_qty))
        total += (self.power.price * Decimal(self.power_qty))
        total += (self.bnc_connector.price * Decimal(self.bnc_qty))
        total += (self.dc_connector.price * Decimal(self.dc_qty))
        total += (self.installation.price * Decimal(self.installation_qty))

        return total

    def __str__(self):
        return f"{self.name} (₹{self.total_price()})"





# # COMBO / PRODUCT (built from masters)
# class ComboProduct(models.Model):
#     name = models.CharField(max_length=150)
#     camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
#     camera_qty = models.PositiveIntegerField(default=2)
#     dvr = models.ForeignKey(DVR, on_delete=models.CASCADE)
#     cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
#     power = models.ForeignKey(PowerSupply, on_delete=models.CASCADE)
#     bnc_connector = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='bnc_in_combo')
#     dc_connector = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='dc_in_combo')
#     installation = models.ForeignKey(InstallationCharge, on_delete=models.CASCADE)
#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # New field
#     created_at = models.DateTimeField(auto_now_add=True)

#     def total_price(self):
#         total = Decimal('0.00')
#         # cameras
#         total += (self.camera.price * Decimal(self.camera_qty))
#         # DVR
#         total += self.dvr.price
#         # Cable
#         total += self.cable.price
#         # Power supply
#         total += self.power.price
#         # connectors
#         total += self.bnc_connector.price + self.dc_connector.price
#         # installation
#         total += self.installation.price
#         return total

#     def __str__(self):
#         return f"{self.name} (₹{self.total_price()})"



# ===== Cart and Order =====
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    combo = models.ForeignKey(ComboProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.combo.total_price() * self.quantity

 
# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     mobile = models.CharField(max_length=15)
#     address = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"Order #{self.id} by {self.name}"



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey('CustomerProfile', on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    combo = models.ForeignKey('ComboProduct', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        if self.combo:
            return f"{self.combo.name} x {self.quantity}"
        else:
            return f"Deleted Product x {self.quantity}"
  


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     combo = models.ForeignKey('ComboProduct', on_delete=models.SET_NULL, null=True)

#     # Snapshot fields
#     product_name = models.CharField(max_length=200)
#     product_image = models.ImageField(upload_to="order_snapshots/", null=True, blank=True)
#     product_description = models.TextField(blank=True)

#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def subtotal(self):
#         return self.quantity * self.price


class CustomerProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name