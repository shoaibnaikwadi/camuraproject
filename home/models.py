# shop/models.py
from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
# from .models import CustomerProfile, Combo


# CAMERA MASTER
# class Camera(models.Model):
#     CAMERA_TYPES = [
#         ('2mp', '2MP'),
#         ('2mp_color', '2MP Color'),
#         ('5mp', '5MP'),
#         ('5mp_color', '5MP Color'),
#     ]
#     camera_type = models.CharField(max_length=30, choices=CAMERA_TYPES)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.get_camera_type_display()} (₹{self.price})"




class Camera(models.Model):
    camera_type = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=5)


    def __str__(self):
        return f"{self.camera_type} (₹{self.price})"
    
class CameraBullet(models.Model):
    bullet_camera_type = models.CharField(max_length=100)
    bullet_model_number = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=5)


    def __str__(self):
        return f"{self.bullet_camera_type} (₹{self.price})"


# DVR MASTER

class DVR(models.Model):
    dvr_name = models.CharField(
        max_length=100,
        help_text="Enter DVR name (e.g., CP Plus 8 Channel DVR)"
    )
    model_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    stock = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.dvr_name} - ₹{self.price}"





class HardDisk(models.Model):
    size = models.CharField(max_length=50)   # e.g., 1TB, 2TB
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.size} HDD (₹{self.price})"

# CABLE MASTER
class Cable(models.Model):
    length = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.length} (₹{self.price})"


# POWER SUPPLY MASTER
class PowerSupply(models.Model):
   
    range_slug = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.range_slug} (₹{self.price})"


# ACCESSORY MASTER (BNC, DC, etc.)
class Accessory(models.Model):
    name = models.CharField(max_length=100)  # e.g., "BNC Connector", "DC Connector"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.name} (₹{self.price})"


# INSTALLATION CHARGES MASTER
class InstallationCharge(models.Model):
    description = models.CharField(max_length=200, default="Installation")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} (₹{self.price})"






from decimal import Decimal


# # COMBO / PRODUCT (built from masters)
# class ComboProduct(models.Model):
#     name = models.CharField(max_length=150)
#     mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


#     camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
#     camera_qty = models.PositiveIntegerField(default=2)
    
#     cameraBullet = models.ForeignKey(CameraBullet, on_delete=models.SET_NULL, null=True, blank=True)   
#     camerabullet_qty = models.PositiveIntegerField(default=1)

#     dvr = models.ForeignKey(DVR, on_delete=models.CASCADE)

#     # hard_disk = models.ForeignKey(HardDisk, on_delete=models.SET_NULL, null=True, blank=True)
#     # hard_disk_qty = models.PositiveIntegerField(default=1)

#     hard_disk = models.ForeignKey(HardDisk, on_delete=models.CASCADE, null=True, blank=True)
#     hard_disk_qty = models.PositiveIntegerField(default=1)

#     cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
#     cable_qty = models.PositiveIntegerField(default=1)   # NEW

#     power = models.ForeignKey(PowerSupply, on_delete=models.CASCADE)
#     power_qty = models.PositiveIntegerField(default=1)   # NEW

#     bnc_connector = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='bnc_in_combo')
#     bnc_qty = models.PositiveIntegerField(default=2)     # NEW

#     dc_connector = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='dc_in_combo')
#     dc_qty = models.PositiveIntegerField(default=2)      # NEW

#     installation = models.ForeignKey(InstallationCharge, on_delete=models.CASCADE)
#     installation_qty = models.PositiveIntegerField(default=1)  # NEW

#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to='product_images/', null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     # def total_price(self):
#     #     total = Decimal('0.00')

#     #     total += (self.camera.price * Decimal(self.camera_qty))
#     #     total += self.dvr.price
#     #     total += (self.cable.price * Decimal(self.cable_qty))
#     #     total += (self.power.price * Decimal(self.power_qty))
#     #     total += (self.bnc_connector.price * Decimal(self.bnc_qty))
#     #     total += (self.dc_connector.price * Decimal(self.dc_qty))
#     #     total += (self.installation.price * Decimal(self.installation_qty))

#     #     return total



#     def total_price(self):
#         total = Decimal('0.00')

#         # Camera
#         total += Decimal(self.camera.price) * self.camera_qty

#         # Camera Bullet (optional)
#         if self.cameraBullet:
#             total += Decimal(self.cameraBullet.price) * self.camerabullet_qty

#         # DVR
#         total += Decimal(self.dvr.price)

#         # Hard Disk (optional)
#         if self.hard_disk:
#             total += Decimal(self.hard_disk.price) * self.hard_disk_qty

#         #   Cable
#         total += Decimal(self.cable.price) * self.cable_qty

#         # Power Supply
#         total += Decimal(self.power.price) * self.power_qty

#         # BNC Connector
#         total += Decimal(self.bnc_connector.price) * self.bnc_qty

#         # DC Connector
#         total += Decimal(self.dc_connector.price) * self.dc_qty

#         # Installation
#         total += Decimal(self.installation.price) * self.installation_qty

#         return total


#         @property
#         def total_price(self):
#             return self._calculate_total_price()

#         def __str__(self):
#             return f"{self.name} (₹{self.total_price})"

#         @property
#         def discount_percentage(self):
#             if self.mrp and self.total_price():
#                 return int((self.mrp - self.total_price()) / self.mrp * 100)
#         return 0






from decimal import Decimal
from django.db import models

# class ComboProduct(models.Model):
#     name = models.CharField(max_length=150)
#     mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     stock = models.PositiveIntegerField(default=0)

#     brand = models.CharField(max_length=100, default="Unknown")


#     camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
#     camera_qty = models.PositiveIntegerField(default=2)
    
#     cameraBullet = models.ForeignKey(CameraBullet, on_delete=models.SET_NULL, null=True, blank=True)   
#     camerabullet_qty = models.PositiveIntegerField(default=1)

#     dvr = models.ForeignKey(DVR, on_delete=models.CASCADE)

#     hard_disk = models.ForeignKey(HardDisk, on_delete=models.CASCADE, null=True, blank=True)
#     hard_disk_qty = models.PositiveIntegerField(default=1)

#     cable = models.ForeignKey(Cable, on_delete=models.CASCADE)
#     cable_qty = models.PositiveIntegerField(default=1)

#     power = models.ForeignKey(PowerSupply, on_delete=models.CASCADE)
#     power_qty = models.PositiveIntegerField(default=1)

#     bnc_connector = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='bnc_in_combo')
#     bnc_qty = models.PositiveIntegerField(default=2)

#     dc_connector = models.ForeignKey(Accessory, on_delete=models.CASCADE, related_name='dc_in_combo')
#     dc_qty = models.PositiveIntegerField(default=2)

#     installation = models.ForeignKey(InstallationCharge, on_delete=models.CASCADE)
#     installation_qty = models.PositiveIntegerField(default=1)

#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to='product_images/', null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def total_price(self):
#         total = Decimal('0.00')
#         total += Decimal(self.camera.price) * self.camera_qty
#         if self.cameraBullet:
#             total += Decimal(self.cameraBullet.price) * self.camerabullet_qty
#         total += Decimal(self.dvr.price)
#         if self.hard_disk:
#             total += Decimal(self.hard_disk.price) * self.hard_disk_qty
#         total += Decimal(self.cable.price) * self.cable_qty
#         total += Decimal(self.power.price) * self.power_qty
#         total += Decimal(self.bnc_connector.price) * self.bnc_qty
#         total += Decimal(self.dc_connector.price) * self.dc_qty
#         total += Decimal(self.installation.price) * self.installation_qty
#         return total

#     def __str__(self):
#         return f"{self.name} (₹{self.total_price()})"

#     @property
#     def discount_percentage(self):
#         if self.mrp and self.total_price():
#             return int((self.mrp - self.total_price()) / self.mrp * 100)
#         return 0











from django.db import models
from decimal import Decimal


class ComboProduct(models.Model):
    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100, default="Unknown")

    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # ---- COMPONENTS ----

    camera = models.ForeignKey(
        'Camera',
        on_delete=models.CASCADE
    )
    camera_qty = models.PositiveIntegerField(default=2)

    cameraBullet = models.ForeignKey(
        'CameraBullet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    camerabullet_qty = models.PositiveIntegerField(default=1)

    dvr = models.ForeignKey(
        'DVR',
        on_delete=models.CASCADE
    )

    hard_disk = models.ForeignKey(
        'HardDisk',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    hard_disk_qty = models.PositiveIntegerField(default=1)

    cable = models.ForeignKey(
        'Cable',
        on_delete=models.CASCADE
    )
    cable_qty = models.PositiveIntegerField(default=1)

    power = models.ForeignKey(
        'PowerSupply',
        on_delete=models.CASCADE
    )
    power_qty = models.PositiveIntegerField(default=1)

    bnc_connector = models.ForeignKey(
        'Accessory',
        on_delete=models.CASCADE,
        related_name='bnc_combo_products'
    )
    bnc_qty = models.PositiveIntegerField(default=2)

    dc_connector = models.ForeignKey(
        'Accessory',
        on_delete=models.CASCADE,
        related_name='dc_combo_products'
    )
    dc_qty = models.PositiveIntegerField(default=2)

    installation = models.ForeignKey(
        'InstallationCharge',
        on_delete=models.CASCADE
    )
    installation_qty = models.PositiveIntegerField(default=1)

    # ---- DISPLAY ----

    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='product_images/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # ---- PRICE LOGIC ----

    def total_price(self):
        total = Decimal('0.00')

        total += self.camera.price * self.camera_qty

        if self.cameraBullet:
            total += self.cameraBullet.price * self.camerabullet_qty

        total += self.dvr.price

        if self.hard_disk:
            total += self.hard_disk.price * self.hard_disk_qty

        total += self.cable.price * self.cable_qty
        total += self.power.price * self.power_qty
        total += self.bnc_connector.price * self.bnc_qty
        total += self.dc_connector.price * self.dc_qty
        total += self.installation.price * self.installation_qty

        return total

    # ---- STOCK LOGIC (DERIVED) ----

    @property
    def available_stock(self):
        stocks = [
            self.camera.stock // self.camera_qty,
            self.dvr.stock,
            self.cable.stock // self.cable_qty,
            self.power.stock // self.power_qty,
            self.bnc_connector.stock // self.bnc_qty,
            self.dc_connector.stock // self.dc_qty,
        ]

        if self.cameraBullet:
            stocks.append(
                self.cameraBullet.stock // self.camerabullet_qty
            )

        if self.hard_disk:
            stocks.append(
                self.hard_disk.stock // self.hard_disk_qty
            )

        return min(stocks)

    # ---- HELPERS ----

    @property
    def in_stock(self):
        return self.available_stock > 0

    @property
    def discount_percentage(self):
        if self.mrp:
            return int((self.mrp - self.total_price()) / self.mrp * 100)
        return 0

    def __str__(self):
        return f"{self.name} (₹{self.total_price()})"








class ProductReview(models.Model):
    product = models.ForeignKey(ComboProduct, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i,i) for i in range(1,6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)






# ===== Cart and Order =====
# class CartItem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     combo = models.ForeignKey(ComboProduct, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)

#     def subtotal(self):
#         return self.combo.total_price() * self.quantity

from django.core.exceptions import ValidationError

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    combo = models.ForeignKey(ComboProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.quantity > self.combo.available_stock:
            raise ValidationError(
                f"Only {self.combo.available_stock} items available"
            )

    def subtotal(self):
        return self.combo.total_price() * self.quantity

    def __str__(self):
        return f"{self.combo.name} x {self.quantity}"

 




# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     profile = models.ForeignKey('CustomerProfile', on_delete=models.SET_NULL, null=True)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
#     payment_id = models.CharField(max_length=100, blank=True, null=True)
#     payment_status = models.CharField(max_length=50, default='Pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order #{self.id} - {self.user.username}"




class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey('CustomerProfile', on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"



# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     combo = models.ForeignKey('ComboProduct', on_delete=models.SET_NULL, null=True)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def subtotal(self):
#         return self.quantity * self.price

#     def __str__(self):
#         if self.combo:
#             return f"{self.combo.name} x {self.quantity}"
#         else:
#             return f"Deleted Product x {self.quantity}"
  




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    combo = models.ForeignKey(ComboProduct, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        if self.combo:
            return f"{self.combo.name} x {self.quantity}"
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





from django.db import models

# class CCTVEngineer(models.Model):
#     full_name = models.CharField(max_length=100)
#     mobile = models.CharField(max_length=15, unique=True)
#     email = models.EmailField(unique=True)
#     experience = models.CharField(max_length=50)
#     city = models.CharField(max_length=100)
#     address = models.TextField()
#     government_id = models.FileField(upload_to='engineer_ids/', blank=False, null=False)  # 🆕 NEW FIELD
#     certified = models.BooleanField(default=False)
#     date_registered = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.full_name

from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class CCTVEngineer(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('hold', 'Hold'),
    )

    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    experience = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    address = models.TextField()
    government_id = models.FileField(upload_to='engineer_ids/')
    certified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_registered = models.DateTimeField(auto_now_add=True, editable=False)

    def save(self, *args, **kwargs):
        # compress ONLY if image
        if self.government_id:
            file = self.government_id
            file_ext = file.name.split('.')[-1].lower()

            if file_ext in ['jpg', 'jpeg', 'png']:
                img = Image.open(file)

                # convert PNG to RGB (JPEG-friendly)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=70)  # compress to 70%
                buffer.seek(0)

                self.government_id = ContentFile(
                    buffer.read(),
                    name=f"{file.name.split('.')[0]}_compressed.jpg"
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
