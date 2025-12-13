from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.blog_list, name="blog_list"),
    path('category/<slug:slug>/', views.category_posts, name="category_posts"),
    path('search/', views.blog_search, name="blog_search"),
    path('<slug:slug>/', views.blog_detail, name="blog_detail"),
    # path('ckeditor/', include('ckeditor_uploader.urls')),

]
