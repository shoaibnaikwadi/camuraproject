from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Prevent duplicate slug errors
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_category", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name



from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    
    # SEO Fields
    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)

    content = RichTextField()
    featured_image = models.ImageField(upload_to="blog/images/")
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    tags = models.CharField(max_length=200, help_text="Comma-separated tags")
    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Auto-fill SEO fields if empty
        if not self.meta_title:
            self.meta_title = self.title

        if not self.meta_description:
            self.meta_description = self.short_description[:150]

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title
