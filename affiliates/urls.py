from django.urls import path

from . import views

app_name = "affiliate"

urlpatterns = [
    path("", views.affiliate_dashboard, name="dashboard"),
    path("apply/", views.affiliate_apply, name="apply"),
]