from django.contrib import admin
from .models import Category, BlogPost, BlogPostSection


class BlogPostSectionInline(admin.StackedInline):
    model = BlogPostSection
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'created_at']
    list_editable = ['is_published']
    list_filter = ['is_published', 'category']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    inlines = [BlogPostSectionInline]

