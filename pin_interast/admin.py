from django.contrib import admin
from django.utils.html import format_html
from .models import PinBoard, Pin, PinAudioTrack


class PinInline(admin.StackedInline):
    model = Pin
    extra = 1
    fields = ('title', 'image', 'image_url', 'description', 'source_url', 'tags', 'is_published')
    show_change_link = True


@admin.register(PinBoard)
class PinBoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'pinterest_username', 'pinterest_owner_name', 'board_cover_preview', 'pin_count_display', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description', 'pinterest_username', 'pinterest_owner_name']
    inlines = [PinInline]

    @admin.display(description='Cover')
    def board_cover_preview(self, obj):
        url = obj.cover_image_url
        if url:
            return format_html('<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:6px;">', url)
        return '—'

    @admin.display(description='Pins')
    def pin_count_display(self, obj):
        return obj.pin_count


@admin.register(Pin)
class PinAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'pin_image_preview', 'is_published', 'pinterest_pin_id', 'created_at']
    list_editable = ['is_published']
    list_filter = ['is_published', 'board']
    search_fields = ['title', 'description', 'tags']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'board', 'description', 'tags', 'is_published')
        }),
        ('Image', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image from your computer OR paste an image URL. '
                           'If both are set, the uploaded file takes priority.',
        }),
        ('Links & API', {
            'fields': ('source_url', 'pinterest_pin_id'),
        }),
    )

    @admin.display(description='Preview')
    def pin_image_preview(self, obj):
        url = obj.pin_image_url
        if url:
            return format_html('<img src="{}" style="width:60px;height:60px;object-fit:cover;border-radius:8px;">', url)
        return '—'


@admin.register(PinAudioTrack)
class PinAudioTrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'genre', 'cover_preview', 'is_favorite', 'duration', 'board', 'created_at']
    list_editable = ['is_favorite']
    list_filter = ['is_favorite', 'genre', 'board']
    search_fields = ['title', 'artist', 'genre']
    fieldsets = (
        ('Track Info', {
            'fields': ('title', 'artist', 'board', 'genre', 'duration', 'is_favorite', 'order')
        }),
        ('Audio Source', {
            'fields': ('audio_file', 'audio_url'),
            'description': 'Upload an audio file (MP3/WAV) OR paste a direct audio URL.',
        }),
        ('Cover Artwork', {
            'fields': ('cover_image', 'cover_url'),
            'description': 'Upload an image file OR paste an image URL for the album artwork.',
        }),
    )

    @admin.display(description='Cover')
    def cover_preview(self, obj):
        url = obj.cover_art_url
        if url:
            return format_html('<img src="{}" style="width:45px;height:45px;object-fit:cover;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.2);">', url)
        return '—'
