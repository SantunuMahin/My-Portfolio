import math
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import BlogPost, Category


def blog_list(request):
    """List published blog posts with search, category filtering, and pagination."""
    all_posts = BlogPost.objects.filter(is_published=True).select_related('category')
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__is_published=True))
    )
    
    selected_category = request.GET.get('category', '').strip()
    q = request.GET.get('q', '').strip()
    
    posts_qs = all_posts
    if selected_category:
        posts_qs = posts_qs.filter(category__slug=selected_category)
    if q:
        posts_qs = posts_qs.filter(
            Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q)
        )
        
    paginator = Paginator(posts_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'total_count': all_posts.count(),
        'q': q,
    }
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, slug):
    """View blog post details with reading time and related posts."""
    post = get_object_or_404(BlogPost.objects.prefetch_related('sections'), slug=slug, is_published=True)
    
    # Calculate estimated reading time (average 200 words per minute)
    all_text = post.content + ' ' + ' '.join(
        (s.content or '') for s in post.sections.all()
    )
    word_count = len(all_text.split())
    reading_time_mins = max(1, math.ceil(word_count / 200))
    
    related = BlogPost.objects.filter(
        is_published=True, category=post.category
    ).exclude(pk=post.pk)[:3]
    
    context = {
        'post': post,
        'related': related,
        'reading_time_mins': reading_time_mins,
        'word_count': word_count,
    }
    return render(request, 'blog/blog_detail.html', context)
