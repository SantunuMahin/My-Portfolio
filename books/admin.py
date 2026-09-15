from django.contrib import admin
from .models import BookReflection, BookQuote


class BookQuoteInline(admin.StackedInline):
    model = BookQuote
    extra = 1


@admin.register(BookReflection)
class BookReflectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'rating', 'has_favorite_quote', 'has_reflection', 'is_published', 'read_date']
    list_editable = ['status', 'is_published']
    list_filter = ['status', 'is_published', 'read_date']
    prepopulated_fields = {'slug': ('title', 'author')}
    search_fields = ['title', 'author', 'key_takeaway', 'favorite_quote', 'reflection']
    date_hierarchy = 'read_date'
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BookQuoteInline]
    fieldsets = [
        ('Book details', {
            'fields': ['title', 'slug', 'author', 'cover', 'cover_url', 'status', 'rating', 'read_date'],
        }),
        ('Personal notes', {
            'fields': ['key_takeaway', 'favorite_quote', 'reflection'],
            'description': 'Write the quote you want to remember and your own thoughts after reading.',
        }),
        ('Publishing', {
            'fields': ['is_published', 'created_at', 'updated_at'],
        }),
    ]

    @admin.display(boolean=True, description='Quote')
    def has_favorite_quote(self, obj):
        return bool(obj.favorite_quote)

    @admin.display(boolean=True, description='Reflection')
    def has_reflection(self, obj):
        return bool(obj.reflection)

