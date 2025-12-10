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




# from django import forms
# from .models import CCTVEngineer

# class CCTVEngineerForm(forms.ModelForm):
#     class Meta:
#         model = CCTVEngineer
#         fields = ['full_name', 'mobile', 'email', 'experience', 'city', 'address', 'certified']

#         widgets = {
#             'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
#             'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9876543210'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
#             'experience': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 3 Years'}),
#             'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mumbai, Delhi'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'certified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }



# from django import forms
# from .models import CCTVEngineer

# class CCTVEngineerForm(forms.ModelForm):
#     class Meta:
#         model = CCTVEngineer
#         fields = [
#             'full_name', 'mobile', 'email', 'experience',
#             'city', 'address', 'government_id', 'certified'
#         ]

#         widgets = {
#             'full_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'mobile': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'experience': forms.TextInput(attrs={'class': 'form-control'}),
#             'city': forms.TextInput(attrs={'class': 'form-control'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'certified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }




from django import forms
from .models import CCTVEngineer
import os

class CCTVEngineerForm(forms.ModelForm):

    def clean_government_id(self):
        file = self.cleaned_data.get("government_id")

        if file:
            ext = os.path.splitext(file.name)[1].lower()

            allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']

            # Validate file type
            if ext not in allowed_extensions:
                raise forms.ValidationError("Only JPG, JPEG, PNG and PDF files are allowed.")

            # Validate file size < 5 MB
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 5MB.")

        return file

    class Meta:
        model = CCTVEngineer
        fields = [
            'full_name', 'mobile', 'email', 'experience',
            'city', 'address', 'government_id', 'certified',
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'certified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
