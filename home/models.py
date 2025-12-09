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









# ===== Cart and Order =====
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    combo = models.ForeignKey(ComboProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.combo.total_price() * self.quantity

 




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
  



# now this is used for addresses
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
    



from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.full_name if self.full_name else self.mobile
 




class ServiceBooking(models.Model):
    SERVICE_TYPES = [
        ("cctvrepair", "CCTV Repair"),
        # ("desotherktop", "Other Repair"),
        # ("onsite", "On-site Visit"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    problem_description = models.TextField()

    service_type = models.CharField(
        max_length=20, choices=SERVICE_TYPES, default="onsite"
    )

    preferred_date = models.DateField()
    preferred_time = models.TimeField()

    address = models.TextField(blank=True, null=True)

    attachment = models.FileField(upload_to="service_attachments/", blank=True, null=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.mobile}"
