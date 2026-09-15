from django.db import models
from django.utils.text import slugify


class PinBoard(models.Model):
    """A named collection / board that groups Pins together."""
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    description = models.TextField(blank=True, help_text="Short description shown on the board card")
    cover_image = models.ImageField(
        upload_to='pin_interast/boards/',
        blank=True, null=True,
        help_text="Upload a cover image from your computer"
    )
    cover_url = models.URLField(
        max_length=1000, blank=True, null=True,
        help_text="Or paste an online image URL for the cover"
    )
    pinterest_username = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Pinterest username of the board owner (e.g. 'nasa')"
    )
    pinterest_owner_name = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="Display name of the Pinterest board owner"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pin Board'
        verbose_name_plural = 'Pin Boards'

    def __str__(self):
        return self.name

    @property
    def cover_image_url(self):
        if self.cover_image:
            return self.cover_image.url
        elif self.cover_url:
            return self.cover_url
        return None

    @property
    def pin_count(self):
        return self.pins.filter(is_published=True).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'board'
            slug = base_slug
            counter = 2
            while PinBoard.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('pin_interast:board_detail', kwargs={'slug': self.slug})


class Pin(models.Model):
    """A single pinned image, optionally linked to a PinBoard."""
    board = models.ForeignKey(
        PinBoard, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pins'
    )
    title = models.CharField(max_length=300,blank=True)
    description = models.TextField(blank=True, help_text="Optional caption / notes about the pin")

    # Image: upload from computer OR paste a URL
    image = models.ImageField(
        upload_to='pin_interast/pins/',
        blank=True, null=True,
        help_text="Upload an image from your computer"
    )
    image_url = models.URLField(
        max_length=1000, blank=True, null=True,
        help_text="Or paste a direct image URL (JPEG, PNG, WebP…)"
    )

    source_url = models.URLField(
        max_length=1000, blank=True, null=True,
        help_text="Original source link (website, article, etc.)"
    )
    tags = models.CharField(
        max_length=500, blank=True,
        help_text="Comma-separated tags, e.g. 'design, typography, dark-ui'"
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Pinterest API integration field
    pinterest_pin_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True,
        help_text="Pinterest pin ID — set automatically when imported via API"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pin'
        verbose_name_plural = 'Pins'

    def __str__(self):
        return self.title or f"Pin #{self.pk or 'new'}"

    @property
    def pin_image_url(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None

    @property
    def tag_list(self):
        """Returns a list of stripped tag strings."""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_absolute_url(self):
        from django.urls import reverse
        board_slug = self.board.slug if self.board else 'all'
        return reverse('pin_interast:pin_detail', kwargs={'board_slug': board_slug, 'pk': self.pk})


class PinAudioTrack(models.Model):
    """An audio / music track in the Pin Interast Music Lounge."""
    title = models.CharField(max_length=255, help_text="Song / track title")
    artist = models.CharField(max_length=255, default='Santunu Kaysar', help_text="Artist, composer, or creator")
    board = models.ForeignKey(
        PinBoard, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audio_tracks',
        help_text="Optional associated pin board"
    )

    # Audio source: File upload OR streaming/audio URL
    audio_file = models.FileField(
        upload_to='pin_interast/audio/',
        blank=True, null=True,
        help_text="Upload an audio file (MP3, WAV, OGG)"
    )
    audio_url = models.URLField(
        max_length=1000, blank=True, null=True,
        help_text="Or direct URL to audio file/stream (MP3, etc.)"
    )

    # Cover image source: File upload OR image URL
    cover_image = models.ImageField(
        upload_to='pin_interast/music_covers/',
        blank=True, null=True,
        help_text="Upload cover artwork from your computer"
    )
    cover_url = models.URLField(
        max_length=1000, blank=True, null=True,
        help_text="Or direct online image URL for cover artwork"
    )

    is_favorite = models.BooleanField(
        default=False,
        help_text="Mark as favorite in your music list"
    )
    genre = models.CharField(
        max_length=100, blank=True, default='Lo-Fi / Ambient',
        help_text="Genre, mood, or style"
    )
    duration = models.CharField(
        max_length=20, blank=True, default='0:00',
        help_text="Duration string (e.g. '3:20')"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in the playlist"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_favorite', 'order', '-created_at']
        verbose_name = 'Pin Audio Track'
        verbose_name_plural = 'Pin Audio Tracks'

    def __str__(self):
        return f"{self.title} - {self.artist}"

    @property
    def cover_art_url(self):
        if self.cover_image:
            return self.cover_image.url
        elif self.cover_url:
            return self.cover_url
        return "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=600&q=80"

    @property
    def stream_url(self):
        if self.audio_file:
            return self.audio_file.url
        elif self.audio_url:
            return self.audio_url
        return None

    def to_dict(self):
        return {
            'id': self.pk,
            'title': self.title,
            'artist': self.artist,
            'cover_art_url': self.cover_art_url,
            'stream_url': self.stream_url,
            'is_favorite': self.is_favorite,
            'genre': self.genre or 'Lo-Fi / Ambient',
            'duration': self.duration or '0:00',
            'board_name': self.board.name if self.board else None,
        }

