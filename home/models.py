from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from PIL import Image


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    class ProductType(models.TextChoices):
        SINGLE = "single", "Individual Product"
        COMBO = "combo", "Combo Kit"
        
    class CameraType(models.TextChoices):
        HD = "hd", "HD Camera"
        IP = "ip", "IP Camera"
        COMMERCIAL = "Commercial", "Commercial"


    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )

    product_type = models.CharField(
        max_length=10,
        choices=ProductType.choices,
        default=ProductType.SINGLE,
        db_index=True,
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Brand name, e.g. Hikvision, Dahua, CP Plus",
    )

    camera_type = models.CharField(
        max_length=10,
        choices=CameraType.choices,
        blank=True,
        default="",
        db_index=True,
        help_text="Choose HD or IP for cameras and combo kits.",
    )

    camera_quantity = models.PositiveSmallIntegerField(
        default=0,
        db_index=True,
        help_text=(
            "Total cameras included in this product or combo. "
            "For example, enter 4 for a four-camera kit."
        ),
    )

    # Stock is maintained for individual products.
    # Combo availability is calculated from its components.
    stock = models.PositiveIntegerField(default=0)

    main_image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="product_price_nonnegative",
            ),
        ]

    @property
    def available_stock(self):
        if self.product_type == self.ProductType.SINGLE:
            return self.stock

        components = list(
            self.components.select_related("component").all()
        )

        if not components:
            return 0

        if any(item.quantity <= 0 for item in components):
            return 0

        return min(
            item.component.stock // item.quantity
            for item in components
        )

    def clean(self):
        super().clean()

        if self.product_type == self.ProductType.COMBO and self.pk:
            # Combo stock is calculated from its components.
            return

    def __str__(self):
        return self.name


class ComboComponent(models.Model):
    """Individual products and quantities included in a combo."""

    combo = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="components",
        limit_choices_to={
            "product_type": Product.ProductType.COMBO
        },
    )

    component = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="included_in_combos",
        limit_choices_to={
            "product_type": Product.ProductType.SINGLE
        },
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["combo", "component"],
                name="unique_combo_component",
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=1),
                name="combo_component_quantity_positive",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.combo_id
            and self.combo.product_type != Product.ProductType.COMBO
        ):
            raise ValidationError({
                "combo": "Choose a product marked as a combo kit."
            })

        if (
            self.component_id
            and self.component.product_type
            != Product.ProductType.SINGLE
        ):
            raise ValidationError({
                "component": (
                    "Combo components must be individual products."
                )
            })

        if (
            self.combo_id
            and self.component_id
            and self.combo_id == self.component_id
        ):
            raise ValidationError("A combo cannot contain itself.")

    def __str__(self):
        return (
            f"{self.combo.name}: "
            f"{self.component.name} x {self.quantity}"
        )


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    @property
    def product_name(self):
        return self.product.name

    @property
    def unit_price(self):
        return self.product.price

    @property
    def available_stock(self):
        return self.product.available_stock

    def subtotal(self):
        return self.unit_price * self.quantity

    def clean(self):
        super().clean()

        if self.quantity < 1:
            raise ValidationError({
                "quantity": "Quantity must be at least 1."
            })

        if (
            self.product_id
            and self.quantity > self.product.available_stock
        ):
            raise ValidationError({
                "quantity": (
                    f"Only {self.product.available_stock} available."
                )
            })

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("online", "Online Payment"),
        ("cod", "Cash on Delivery"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
    ]

    ORDER_STATUS_CHOICES = [
        ("Received", "Received"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    profile = models.ForeignKey(
        "CustomerProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default="online",
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    payment_status = models.CharField(
        max_length=50,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending",
    )

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="Received",
    )
    stock_deducted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        return sum(
            (item.subtotal() for item in self.items.all()),
            Decimal("0.00"),
        )

    def __str__(self):
        return f"Order #{self.pk} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    # Preserve order history if the product is deleted.
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )

    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)
    product_details = models.JSONField(default=dict, blank=True)

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    def subtotal(self):
        return self.quantity * self.price

    def clean(self):
        super().clean()

        if not self.product_id and not self.product_name:
            raise ValidationError(
                "A product or saved product name is required."
            )

    def save(self, *args, **kwargs):
        if self.product_id:
            if not self.product_name:
                self.product_name = self.product.name

            if not self.product_sku:
                self.product_sku = self.product.sku

            if not self.product_details:
                self.product_details = {
                    "product_type": self.product.product_type,
                    "category": (
                        self.product.category.name
                        if self.product.category_id
                        else ""
                    ),
                }

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.product_name or 'Deleted Product'} "
            f"x {self.quantity}"
        )


class CustomerProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
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


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.full_name or self.mobile


class ServiceBooking(models.Model):
    SERVICE_TYPES = [
        ("cctvrepair", "CCTV Repair Rs. 2000"),
        ("computerrepair", "Computer Repair Rs. 1000"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_bookings",
    )

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    problem_description = models.TextField()

    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPES,
        default="cctvrepair",
    )

    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    address = models.TextField(blank=True, null=True)

    attachment = models.FileField(
        upload_to="service_attachments/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.mobile}"


class CCTVEngineer(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("hold", "Hold"),
    ]

    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    experience = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    address = models.TextField()
    government_id = models.FileField(upload_to="engineer_ids/")
    certified = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    date_registered = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    def save(self, *args, **kwargs):
        if self.government_id:
            file = self.government_id
            ext = file.name.rsplit(".", 1)[-1].lower()

            if ext in {"jpg", "jpeg", "png"}:
                try:
                    img = Image.open(file)

                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=70)
                    buffer.seek(0)

                    self.government_id = ContentFile(
                        buffer.read(),
                        name=(
                            f"{file.name.rsplit('.', 1)[0]}"
                            "_compressed.jpg"
                        ),
                    )

                except (OSError, ValueError):
                    pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class JobOpening(models.Model):
    JOB_TYPE_CHOICES = [
        ("Full Time", "Full Time"),
        ("Part Time", "Part Time"),
        ("Contract", "Contract"),
        ("Internship", "Internship"),
    ]

    title = models.CharField(max_length=150)
    location = models.CharField(max_length=100)

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default="Full Time",
    )

    experience = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    salary = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    vacancies = models.PositiveIntegerField(default=1)
    last_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title