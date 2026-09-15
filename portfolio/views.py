from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Profile, Experience, Education, SkillCategory, Project, Service, Certificate

try:
    from blog.models import BlogPost
except ImportError:
    BlogPost = None

try:
    from books.models import BookReflection
except ImportError:
    BookReflection = None

try:
    from pin_interast.models import Pin, PinBoard
except ImportError:
    Pin = None
    PinBoard = None


def index(request):
    """Single page portfolio - all sections loaded at once."""
    profile = Profile.objects.first()
    experiences = Experience.objects.all()
    education = Education.objects.all()
    certificates = Certificate.objects.all()
    skill_categories = SkillCategory.objects.prefetch_related('skills').all()
    projects = Project.objects.all()
    services = Service.objects.all()
    featured_projects = projects.filter(is_featured=True)

    # For project filter categories
    categories = projects.values_list('category', flat=True).distinct()

    context = {
        'profile': profile,
        'experiences': experiences,
        'education': education,
        'certificates': certificates,
        'skill_categories': skill_categories,
        'projects': projects,
        'services': services,
        'featured_projects': featured_projects,
        'categories': categories,
        'active_tab': 'about',
    }
    return render(request, 'index.html', context)





def get_url_suggestions(path):
    """Analyze a broken URL and return similar URLs or app routes."""
    suggestions = []
    # Clean up segments
    segments = [s.strip().lower() for s in path.split('/') if s.strip()]
    if not segments:
        return suggestions

    first_segment = segments[0]
    
    # Check close matches for main sections
    app_mappings = {
        'blog': ['blog', 'blogs', 'bloog', 'post', 'posts', 'articles', 'article', 'writeup'],
        'books': ['books', 'book', 'reading', 'readings', 'shelf', 'library', 'note', 'notes'],
        'tasks': ['tasks', 'task', 'time', 'tracker', 'planner', 'todo', 'todos', 'timer'],
        'pins': ['pins', 'pin', 'pinterest', 'board', 'boards', 'interast', 'pin_interast', 'interest']
    }
    
    matched_app = None
    for app, keywords in app_mappings.items():
        if first_segment in keywords:
            matched_app = app
            break
            
    if matched_app:
        if matched_app == 'blog':
            suggestions.append({'label': 'Blog Main Listing', 'url': '/blog/', 'icon': 'newspaper-outline'})
        elif matched_app == 'books':
            suggestions.append({'label': 'Book Reading Notes', 'url': '/books/', 'icon': 'book-outline'})
        elif matched_app == 'tasks':
            suggestions.append({'label': 'Task Board & Planner', 'url': '/tasks/', 'icon': 'list-outline'})
        elif matched_app == 'pins':
            suggestions.append({'label': 'Pinterest Inspiration', 'url': '/pins/', 'icon': 'logo-pinterest'})

    # If there is a slug-like segment (usually the last), do a DB query to see if there's a match
    slug_to_match = segments[-1]
    # Split slug by delimiters
    words = [w for w in slug_to_match.replace('-', '_').split('_') if len(w) > 2]
    
    if BlogPost and words:
        post_q = Q()
        for w in words:
            post_q |= Q(slug__icontains=w) | Q(title__icontains=w)
        posts = BlogPost.objects.filter(post_q, is_published=True)[:3]
        for post in posts:
            suggestions.append({
                'label': f"Blog Post: {post.title}",
                'url': post.get_absolute_url(),
                'icon': 'document-text-outline'
            })
            
    if BookReflection and words:
        book_q = Q()
        for w in words:
            book_q |= Q(slug__icontains=w) | Q(title__icontains=w) | Q(author__icontains=w)
        books = BookReflection.objects.filter(book_q, is_published=True)[:3]
        for book in books:
            suggestions.append({
                'label': f"Book Note: {book.title} by {book.author}",
                'url': book.get_absolute_url(),
                'icon': 'book-outline'
            })
            
    if PinBoard and words:
        board_q = Q()
        for w in words:
            board_q |= Q(slug__icontains=w) | Q(name__icontains=w)
        boards = PinBoard.objects.filter(board_q)[:2]
        for b in boards:
            suggestions.append({
                'label': f"Pin Board: {b.name}",
                'url': b.get_absolute_url(),
                'icon': 'folder-open-outline'
            })

    # Fallback to general sections if nothing specific matched
    if not suggestions:
        if any(w in slug_to_match for w in ['contact', 'email', 'message', 'mail']):
            suggestions.append({'label': 'Contact Me Section', 'url': '/#contact', 'icon': 'mail-outline'})
        elif any(w in slug_to_match for w in ['project', 'work', 'portfolio', 'featured']):
            suggestions.append({'label': 'Projects Portfolio', 'url': '/#projects', 'icon': 'code-slash-outline'})
        elif any(w in slug_to_match for w in ['resume', 'cv', 'experience', 'education']):
            suggestions.append({'label': 'My Resume & CV', 'url': '/#resume', 'icon': 'document-text-outline'})

    # Make unique
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s['url'] not in seen:
            seen.add(s['url'])
            unique_suggestions.append(s)
            
    return unique_suggestions[:5]


def search_view(request):
    """Global search across projects, blog posts, books, pins, skills, and certificates."""
    q = request.GET.get('q', '').strip()
    results = {
        'projects': [],
        'blog_posts': [],
        'books': [],
        'pin_boards': [],
        'pins': [],
        'skills': [],
        'certificates': [],
    }
    
    if q:
        # 1. Projects
        results['projects'] = list(Project.objects.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(tech_stack__icontains=q)
        ))
        
        # 2. Blog Posts
        if BlogPost:
            results['blog_posts'] = list(BlogPost.objects.filter(is_published=True).filter(
                Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q)
            ).select_related('category'))
            
        # 3. Book Reflections
        if BookReflection:
            results['books'] = list(BookReflection.objects.filter(is_published=True).filter(
                Q(title__icontains=q) | Q(author__icontains=q) | Q(reflection__icontains=q) | Q(key_takeaway__icontains=q)
            ))
            
        # 4. Pins and Boards
        if PinBoard:
            results['pin_boards'] = list(PinBoard.objects.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            ))
        if Pin:
            results['pins'] = list(Pin.objects.filter(is_published=True).filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(tags__icontains=q)
            ).select_related('board'))

        # 5. Skills
        results['skills'] = list(Skill.objects.filter(
            Q(name__icontains=q) | Q(category__name__icontains=q)
        ).select_related('category'))

        # 6. Certificates
        results['certificates'] = list(Certificate.objects.filter(
            Q(title__icontains=q) | Q(issuer__icontains=q) | Q(description__icontains=q)
        ))

    total_results = (
        len(results['projects']) +
        len(results['blog_posts']) +
        len(results['books']) +
        len(results['pin_boards']) +
        len(results['pins']) +
        len(results['skills']) +
        len(results['certificates'])
    )

    context = {
        'status_code': 200,
        'status_title': f"Search Results for '{q}'" if q else "Search My Site",
        'status_message': f"Found {total_results} matching items." if q else "Search across blog posts, projects, book notes, pins, and skills.",
        'q': q,
        'results': results,
        'total_results': total_results,
    }
    return render(request, 'httpstatus.html', context)


# --- Custom HTTP Error Handlers ---

def page_not_found(request, exception=None):
    """404 Page Not Found view."""
    path = request.path
    suggestions = get_url_suggestions(path)
    response = render(request, 'httpstatus.html', {
        'status_code': 404,
        'status_title': 'Page Not Found',
        'status_message': "The page you are looking for doesn't exist, was removed, or is temporarily unavailable.",
        'suggestions': suggestions,
    })
    response.status_code = 404
    return response


def permission_denied(request, exception=None):
    """403 Forbidden / Permission Denied view."""
    response = render(request, 'httpstatus.html', {
        'status_code': 403,
        'status_title': 'Access Forbidden',
        'status_message': "You do not have administrative or appropriate permissions to access this page.",
    })
    response.status_code = 403
    return response


def bad_request(request, exception=None):
    """400 Bad Request view."""
    response = render(request, 'httpstatus.html', {
        'status_code': 400,
        'status_title': 'Bad Request',
        'status_message': "The request could not be understood by the server due to malformed syntax.",
    })
    response.status_code = 400
    return response


def server_error(request):
    """500 Internal Server Error view."""
    response = render(request, 'httpstatus.html', {
        'status_code': 500,
        'status_title': 'Internal Server Error',
        'status_message': "Something went wrong on our end. We're already working to fix this.",
    })
    response.status_code = 500
    return response


# --- Error Testing Views (for DEBUG=True mode) ---

def test_404(request):
    return page_not_found(request, Exception("Developer Test 404"))


def test_403(request):
    return permission_denied(request, Exception("Developer Test 403"))


def test_500(request):
    return server_error(request)

