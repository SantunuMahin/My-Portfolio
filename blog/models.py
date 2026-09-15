from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'category'
            slug = base_slug
            counter = 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True, max_length=350)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    banner = models.ImageField(upload_to='blog/', blank=True, null=True)
    banner_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Online image URL for the banner")
    excerpt = models.TextField(max_length=500, blank=True, help_text="Short summary shown on listing page")
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def banner_image_url(self):
        if self.banner:
            return self.banner.url
        elif self.banner_url:
            return self.banner_url
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'post'
            slug = base_slug
            counter = 2
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:detail', kwargs={'slug': self.slug})


class BlogPostSection(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Section title / Subheading")
    content = models.TextField(blank=True, null=True, help_text="Section content (supports linebreaks)")
    image = models.ImageField(upload_to='blog/sections/', blank=True, null=True, help_text="Local image upload")
    image_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Online image URL")
    order = models.PositiveIntegerField(default=0, help_text="Display order of this section")

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f"Section {self.order} for {self.post.title}"

    @property
    def section_image_url(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None

