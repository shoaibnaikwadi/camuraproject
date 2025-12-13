from django.contrib import admin
from .models import BlogPost, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "featured", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("category", "featured", "created_at")
    search_fields = ("title", "tags", "short_description")
