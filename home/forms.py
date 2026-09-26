
# shop/forms.py

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Row,
    Column,
    Submit,
)


from django import forms
from .models import (
    Camera,
    CameraBullet,
    DVR,
    HardDisk,
    Cable,
    PowerSupply,
    Accessory,
    InstallationCharge,
    ComboProduct,
    CustomerProfile,
    ServiceBooking,
    CCTVEngineer,
)


# ============================================================
# CAMERA
# ============================================================

class CameraForm(forms.ModelForm):

    class Meta:
        model = Camera

        fields = [
            "camera_type",
            "model_number",
            "price",
            "stock",
        ]

        widgets = {
            "camera_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2MP Dome Camera",
                }
            ),

            "model_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. CP-UNC-TA21L3",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


# ============================================================
# BULLET CAMERA
# ============================================================

class CameraBulletForm(forms.ModelForm):

    class Meta:
        model = CameraBullet

        fields = [
            "bullet_camera_type",
            "bullet_model_number",
            "price",
            "stock",
        ]

        widgets = {
            "bullet_camera_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2MP Bullet Camera",
                }
            ),

            "bullet_model_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. CP-UNC-TB21L3",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


# ============================================================
# DVR
# ============================================================

class DVRForm(forms.ModelForm):

    class Meta:
        model = DVR

        fields = [
            "dvr_name",
            "model_number",
            "price",
            "stock",
        ]

        widgets = {
            "dvr_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. CP Plus 8 Channel DVR",
                }
            ),

            "model_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "DVR model number",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


# ============================================================
# HARD DISK
# ============================================================

class HardDiskForm(forms.ModelForm):

    class Meta:
        model = HardDisk

        fields = [
            "size",
            "price",
            "stock",
        ]

        widgets = {
            "size": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 1TB, 2TB, 4TB",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


# ============================================================
# CABLE
# ============================================================

class CableForm(forms.ModelForm):

    class Meta:
        model = Cable

        fields = [
            "length",
            "price",
            "stock",
        ]

        widgets = {
            "length": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 90 Meter, 305 Meter",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


# ============================================================
# POWER SUPPLY
# ============================================================

class PowerSupplyForm(forms.ModelForm):

    class Meta:
        model = PowerSupply

        fields = [
            "range_slug",
            "price",
            "stock",
        ]

        widgets = {
            "range_slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 12V 5A",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


# ============================================================
# ACCESSORY
# ============================================================

class AccessoryForm(forms.ModelForm):

    class Meta:
        model = Accessory

        fields = [
            "name",
            "price",
            "stock",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. BNC Connector",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


# ============================================================
# INSTALLATION CHARGE
# ============================================================

class InstallationForm(forms.ModelForm):

    class Meta:
        model = InstallationCharge

        fields = [
            "description",
            "price",
        ]

        widgets = {
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. CCTV Installation",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }


# ============================================================
# CCTV COMBO PRODUCT
# ============================================================

class ComboForm(forms.ModelForm):

    class Meta:
        model = ComboProduct

        fields = [
            "name",
            "brand",
            "mrp",

            # Camera
            "camera",
            "camera_qty",

            # Bullet Camera
            "cameraBullet",
            "camerabullet_qty",

            # DVR
            "dvr",

            # Hard Disk
            "hard_disk",
            "hard_disk_qty",

            # Cable
            "cable",
            "cable_qty",

            # Power Supply
            "power",
            "power_qty",

            # BNC
            "bnc_connector",
            "bnc_qty",

            # DC
            "dc_connector",
            "dc_qty",

            # Installation
            "installation",
            "installation_qty",

            # Display
            "description",
            "image",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 4 Camera CCTV Combo Kit",
                }
            ),

            "brand": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. CP Plus",
                }
            ),

            "mrp": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "MRP",
                }
            ),

            "camera": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "camera_qty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "cameraBullet": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "camerabullet_qty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "dvr": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "hard_disk": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "hard_disk_qty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "cable": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "cable_qty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "power": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "power_qty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "bnc_connector": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "bnc_qty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "dc_connector": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "dc_qty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "installation": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "installation_qty": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the CCTV combo kit...",
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


# ============================================================
# CUSTOMER ADDRESS
# ============================================================

class CustomerProfileForm(forms.ModelForm):

    class Meta:
        model = CustomerProfile

        fields = [
            "full_name",
            "email",
            "mobile",
            "address",
            "city",
            "state",
            "pincode",
        ]

        widgets = {

            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full Name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address",
                }
            ),

            "mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mobile Number",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Full Address",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "City",
                }
            ),

            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "State",
                }
            ),

            "pincode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Pincode",
                }
            ),
        }


# ============================================================
# SERVICE BOOKING
# ============================================================

class ServiceBookingForm(forms.ModelForm):

    class Meta:
        model = ServiceBooking

        # Do NOT include:
        # user
        # status
        # amount
        # payment_status
        # razorpay_order_id
        # razorpay_payment_id

        fields = [
            "name",
            "mobile",
            "email",
            "problem_description",
            "service_type",
            "preferred_date",
            "preferred_time",
            "address",
            "attachment",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your Name",
                }
            ),

            "mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mobile Number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address",
                }
            ),

            "problem_description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Describe your problem...",
                }
            ),

            "service_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "preferred_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "preferred_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                    "placeholder": "Service Address",
                }
            ),

            "attachment": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.form_method = "POST"

        self.helper.layout = Layout(

            "name",
            "mobile",
            "email",

            "problem_description",

            "service_type",

            Row(
                Column(
                    "preferred_date",
                    css_class="col-md-6"
                ),

                Column(
                    "preferred_time",
                    css_class="col-md-6"
                ),
            ),

            "address",

            "attachment",

            Submit(
                "submit",
                "Confirm Booking",
                css_class="btn btn-primary w-100 mt-3"
            )
        )


# ============================================================
# CCTV ENGINEER REGISTRATION
# ============================================================

class CCTVEngineerForm(forms.ModelForm):

    def clean_government_id(self):

        file = self.cleaned_data.get("government_id")

        if not file:
            return file

        import os

        ext = os.path.splitext(
            file.name
        )[1].lower()

        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".pdf",
        ]

        if ext not in allowed_extensions:

            raise forms.ValidationError(
                "Only JPG, JPEG, PNG and PDF files are allowed."
            )

        # Maximum 5 MB
        if file.size > 5 * 1024 * 1024:

            raise forms.ValidationError(
                "File size must be less than 5MB."
            )

        return file

    class Meta:

        model = CCTVEngineer

        # status is intentionally NOT included.
        # Admin should control pending/verified/hold.

        fields = [
            "full_name",
            "mobile",
            "email",
            "experience",
            "city",
            "address",
            "government_id",
            "certified",
        ]

        widgets = {

            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full Name",
                }
            ),

            "mobile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mobile Number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address",
                }
            ),

            "experience": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 5 Years",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "City",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Full Address",
                }
            ),

            "government_id": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".jpg,.jpeg,.png,.pdf",
                }
            ),

            "certified": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
