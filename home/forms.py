# shop/forms.py
from django import forms
from .models import Camera, DVR, Cable, PowerSupply, Accessory, InstallationCharge, ComboProduct, CustomerProfile

class CameraForm(forms.ModelForm):
    class Meta:
        model = Camera
        fields = ['camera_type', 'price']

class DVRForm(forms.ModelForm):
    class Meta:
        model = DVR
        fields = ['channels', 'resolution', 'price']

class CableForm(forms.ModelForm):
    class Meta:
        model = Cable
        fields = ['length', 'price']

class PowerSupplyForm(forms.ModelForm):
    class Meta:
        model = PowerSupply
        fields = ['range_slug', 'price']

class AccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['name', 'price']

class InstallationForm(forms.ModelForm):
    class Meta:
        model = InstallationCharge
        fields = ['description', 'price']

class ComboForm(forms.ModelForm):
    class Meta:
        model = ComboProduct
        fields = ['name','camera','camera_qty','dvr','cable','power','bnc_connector','dc_connector','installation','description']


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['full_name', 'email', 'mobile', 'address', 'city', 'state', 'pincode']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


# from django import forms
# from .models import ServiceBooking

# class ServiceBookingForm(forms.ModelForm):
#     class Meta:
#         model = ServiceBooking
#         fields = "__all__"
#         widgets = {
#             "preferred_date": forms.DateInput(attrs={"type": "date"}),
#             "preferred_time": forms.TimeInput(attrs={"type": "time"}),
#             "problem_description": forms.Textarea(attrs={"rows": 3}),
#             "address": forms.Textarea(attrs={"rows": 2}),
#         }



from django import forms
from .models import ServiceBooking
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit


class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = "__all__"

        widgets = {
            "preferred_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "preferred_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "problem_description": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "address": forms.Textarea(
                attrs={"rows": 2, "class": "form-control"}
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
                Column("preferred_date", css_class="col-md-6"),
                Column("preferred_time", css_class="col-md-6"),
            ),

            "address",
            "attachment",

            Submit("submit", "Submit Booking", css_class="btn btn-primary w-100 mt-3")
        )
