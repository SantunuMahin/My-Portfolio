from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class BookReflection(models.Model):
    STATUS_CHOICES = [
        ('reading', 'Reading'),
        ('finished', 'Finished'),
        ('paused', 'Paused'),
        ('want_to_read', 'Want to Read'),
    ]

    title = models.CharField(max_length=240)
    slug = models.SlugField(unique=True, blank=True, max_length=280)
    author = models.CharField(max_length=180)
    cover = models.ImageField(upload_to='books/', blank=True, null=True)
    cover_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Online cover image URL")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='finished')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text='Optional personal rating from 1 to 5.',
    )
    read_date = models.DateField(null=True, blank=True)
    key_takeaway = models.TextField(blank=True, help_text='The main idea you want people to remember.')
    favorite_quote = models.TextField(blank=True)
    reflection = models.TextField(help_text='Your personal thoughts after reading this book.')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-read_date', '-created_at']
        verbose_name = 'Book Reflection'
        verbose_name_plural = 'Book Reflections'

    @property
    def cover_image_url(self):
        if self.cover:
            return self.cover.url
        elif self.cover_url:
            return self.cover_url
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f'{self.title}-{self.author}') or 'book'
            slug = base_slug
            counter = 2
            while BookReflection.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} by {self.author}'

    def get_absolute_url(self):
        return reverse('books:detail', kwargs={'slug': self.slug})

    @property
    def rating_range(self):
        return range(self.rating or 0)

    @property
    def status_class(self):
        return self.status.replace('_', '-')


class BookQuote(models.Model):
    book = models.ForeignKey(BookReflection, on_delete=models.CASCADE, related_name='quotes')
    quote = models.TextField(help_text="The quote text")
    explanation = models.TextField(blank=True, null=True, help_text="Your thoughts/reflections on this quote")
    image = models.ImageField(upload_to='books/quotes/', blank=True, null=True, help_text="Local image upload for this quote")
    image_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Online image URL for this quote")
    order = models.PositiveIntegerField(default=0, help_text="Display order of this quote")

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Quote from {self.book.title} (Order: {self.order})"

    @property
    def quote_image_url(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None

