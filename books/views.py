import math
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from .models import BookReflection


def book_list(request):
    """Shelf list of books and reading notes with search, status filtering, and sorting."""
    all_books = BookReflection.objects.filter(is_published=True)

    counts = all_books.values('status').annotate(total=Count('id'))
    counts_dict = {c['status']: c['total'] for c in counts}
    total_count = all_books.count()
    finished_count = counts_dict.get('finished', 0)
    reading_count = counts_dict.get('reading', 0)
    latest_book = all_books.first()

    status_list = []
    for value, label in BookReflection.STATUS_CHOICES:
        status_list.append({
            'value': value,
            'label': label,
            'count': counts_dict.get(value, 0)
        })

    selected_status = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'recent').strip()

    books = all_books
    if selected_status:
        books = books.filter(status=selected_status)
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(key_takeaway__icontains=q))

    if sort_by == 'rating':
        books = books.order_by('-rating', '-read_date', '-created_at')
    elif sort_by == 'title':
        books = books.order_by('title')
    else:  # recent
        books = books.order_by('-read_date', '-created_at')

    context = {
        'books': books,
        'status_list': status_list,
        'selected_status': selected_status,
        'total_count': total_count,
        'finished_count': finished_count,
        'reading_count': reading_count,
        'latest_book': latest_book,
        'q': q,
        'sort_by': sort_by,
    }
    return render(request, 'books/book_list.html', context)


def book_detail(request, slug):
    """Detail view for a book reflection and quotes."""
    book = get_object_or_404(
        BookReflection.objects.prefetch_related('quotes'),
        slug=slug,
        is_published=True
    )
    
    # Calculate reading time
    all_text = (book.reflection or '') + ' ' + (book.key_takeaway or '') + ' ' + ' '.join(
        (q.quote or '') + ' ' + (q.explanation or '') for q in book.quotes.all()
    )
    word_count = len(all_text.split())
    reading_time_mins = max(1, math.ceil(word_count / 200))

    related = BookReflection.objects.filter(
        is_published=True, status=book.status
    ).exclude(pk=book.pk)[:3]
    
    return render(request, 'books/book_detail.html', {
        'book': book,
        'related': related,
        'reading_time_mins': reading_time_mins,
    })
