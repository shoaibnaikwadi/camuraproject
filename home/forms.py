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