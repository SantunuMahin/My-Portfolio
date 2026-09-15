from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login as auth_login
from .models import PinBoard, Pin, PinAudioTrack


def board_list(request):
    """Show all published boards with pin counts and inspiration audio tracks."""
    boards = PinBoard.objects.all()
    recent_pins = Pin.objects.filter(is_published=True).order_by('-created_at')[:8]
    audio_tracks = PinAudioTrack.objects.all()
    favorite_tracks_count = PinAudioTrack.objects.filter(is_favorite=True).count()
    is_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    context = {
        'boards': boards,
        'recent_pins': recent_pins,
        'total_pins': Pin.objects.filter(is_published=True).count(),
        'audio_tracks': audio_tracks,
        'favorite_tracks_count': favorite_tracks_count,
        'audio_tracks_json': [t.to_dict() for t in audio_tracks],
        'is_admin': is_admin,
    }
    return render(request, 'pin_interast/board_list.html', context)


def board_detail(request, slug):
    """Show all published pins in a board, with optional tag filtering."""
    board = get_object_or_404(PinBoard, slug=slug)
    pins_qs = board.pins.filter(is_published=True)

    selected_tag = request.GET.get('tag', '').strip()
    if selected_tag:
        pins_qs = pins_qs.filter(tags__icontains=selected_tag)

    # Collect unique tags across all published pins in this board
    all_tags = set()
    for pin in board.pins.filter(is_published=True):
        all_tags.update(pin.tag_list)
    all_tags = sorted(all_tags)

    from django.core.paginator import Paginator
    paginator = Paginator(pins_qs, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'board': board,
        'page_obj': page_obj,
        'all_tags': all_tags,
        'selected_tag': selected_tag,
    }
    return render(request, 'pin_interast/board_detail.html', context)


def pin_detail(request, board_slug, pk):
    """Show a single pin with full image and details."""
    pin = get_object_or_404(Pin, pk=pk, is_published=True)
    related_pins = Pin.objects.filter(
        is_published=True, board=pin.board
    ).exclude(pk=pin.pk)[:8]
    context = {
        'pin': pin,
        'related_pins': related_pins,
    }
    return render(request, 'pin_interast/pin_detail.html', context)


def all_pins(request):
    """Show all published pins across all boards (flat masonry grid)."""
    pins_qs = Pin.objects.filter(is_published=True)

    selected_tag = request.GET.get('tag', '').strip()
    if selected_tag:
        pins_qs = pins_qs.filter(tags__icontains=selected_tag)

    # Global tag cloud
    all_tags = set()
    for pin in Pin.objects.filter(is_published=True):
        all_tags.update(pin.tag_list)
    all_tags = sorted(all_tags)

    from django.core.paginator import Paginator
    paginator = Paginator(pins_qs, 24)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'all_tags': all_tags,
        'selected_tag': selected_tag,
        'boards': PinBoard.objects.all(),
    }
    return render(request, 'pin_interast/all_pins.html', context)


def pinterest_import(request):
    """
    Import a public Pinterest board by URL or pasted Page Source.
    Allows authenticated users with proper permission (staff status or pin_interast.add_pinboard permission).
    """
    # Handle logout POST request directly
    if request.method == 'POST' and 'logout' in request.POST:
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, "Logged out successfully.")
        from django.shortcuts import redirect
        return redirect('pin_interast:import')

    if not request.user.is_authenticated:
        # User is not logged in: handle custom authentication form submission
        if request.method == 'POST' and 'login_username' in request.POST:
            username = request.POST.get('login_username', '').strip()
            password = request.POST.get('login_password', '')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Logged in successfully as {username}!")
                from django.shortcuts import redirect
                return redirect('pin_interast:import')
            else:
                messages.error(request, "Invalid username or password.")
                return render(request, 'pin_interast/import_login.html', {})
        else:
            return render(request, 'pin_interast/import_login.html', {})

    # Check permission
    has_permission = request.user.is_staff or request.user.has_perm('pin_interast.add_pinboard')
    if not has_permission:
        # Logged in but not authorized: show pending approval page
        return render(request, 'pin_interast/import_pending.html', {})

    if request.method == 'POST':
        board_url = request.POST.get('board_url', '').strip()
        pasted_source = request.POST.get('pasted_source', '').strip()

        if not board_url:
            messages.error(request, "Please enter a Pinterest board URL.")
            return render(request, 'pin_interast/import_pinterest.html', {})

        try:
            from .pinterest_api import PinterestClient, PinterestAPIError
            client = PinterestClient()
            
            if pasted_source:
                result = client.import_board_from_html(html_content=pasted_source, board_url=board_url)
            else:
                result = client.import_board_to_db(board_url=board_url)
                
            messages.success(
                request,
                f"✅ Import complete! Board: '{result['board'].name}' — "
                f"{result['created']} new, {result['updated']} updated, "
                f"{result['skipped']} skipped (no image)."
            )
            context = {'result': result}
        except Exception as exc:
            messages.error(request, f"Import failed: {exc}")
            context = {'error': str(exc)}

        return render(request, 'pin_interast/import_pinterest.html', context)

    # GET
    return render(request, 'pin_interast/import_pinterest.html', {})


def pinterest_register(request):
    """
    Public registration page for new users.
    Once registered, users can log in, but need to wait for an admin to grant permissions.
    """
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('pin_interast:import')

    if request.method == 'POST':
        username = request.POST.get('reg_username', '').strip()
        email = request.POST.get('reg_email', '').strip()
        password = request.POST.get('reg_password', '')
        password_confirm = request.POST.get('reg_password_confirm', '')
        first_name = request.POST.get('reg_first_name', '').strip()
        last_name = request.POST.get('reg_last_name', '').strip()

        if not (username and email and password and password_confirm):
            messages.error(request, "All fields are required.")
            return render(request, 'pin_interast/register.html', {})

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'pin_interast/register.html', {})

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'pin_interast/register.html', {})

        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return render(request, 'pin_interast/register.html', {})

        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already registered.")
            return render(request, 'pin_interast/register.html', {})

        try:
            # Create active user (not staff, no permissions by default)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_active=True
            )
            messages.success(
                request,
                "Registration successful! Please log in below. "
                "Note: You will need to wait for an administrator to grant you import permissions."
            )
            from django.shortcuts import redirect
            return redirect('pin_interast:import')
        except Exception as exc:
            messages.error(request, f"An error occurred during registration: {exc}")
            return render(request, 'pin_interast/register.html', {})

    return render(request, 'pin_interast/register.html', {})


# ==============================================================================
# AUDIO MUSIC LOUNGE API ENDPOINTS
# ==============================================================================

@require_http_methods(["GET"])
def api_music_tracks(request):
    """Return all audio tracks in JSON format, with optional favorites filter."""
    qs = PinAudioTrack.objects.all()
    if request.GET.get('favorites') in ('1', 'true', 'yes'):
        qs = qs.filter(is_favorite=True)
    board_slug = request.GET.get('board')
    if board_slug:
        qs = qs.filter(board__slug=board_slug)
    tracks = [t.to_dict() for t in qs]
    return JsonResponse({'success': True, 'tracks': tracks})


@require_http_methods(["POST"])
def api_toggle_favorite(request, track_id):
    """Toggle the favorite status of a music track (persisted to DB for admin, acknowledged for visitors)."""
    track = get_object_or_404(PinAudioTrack, pk=track_id)
    user = getattr(request, 'user', None)
    is_staff = bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
    if is_staff:
        track.is_favorite = not track.is_favorite
        track.save(update_fields=['is_favorite'])
        new_status = track.is_favorite
    else:
        new_status = not track.is_favorite

    fav_count = PinAudioTrack.objects.filter(is_favorite=True).count()
    return JsonResponse({
        'success': True,
        'id': track.pk,
        'is_favorite': new_status,
        'favorite_count': fav_count,
        'is_admin': is_staff,
        'message': f"'{track.title}' {'added to' if new_status else 'removed from'} favorites."
    })


@require_http_methods(["POST"])
def api_add_music_track(request):
    """Add a new music track via AJAX (strictly requires administrator / staff permission)."""
    user = getattr(request, 'user', None)
    if not (user and user.is_authenticated and (user.is_staff or user.is_superuser)):
        return JsonResponse({
            'success': False,
            'error': 'Admin authorization required. Only portfolio administrators can add new music tracks.',
            'requires_admin': True,
            'login_url': '/admin/login/?next=/pin-interast/'
        }, status=403)

    title = request.POST.get('title', '').strip()
    if not title:
        return JsonResponse({'success': False, 'error': 'Track title is required.'}, status=400)

    artist = request.POST.get('artist', '').strip() or 'Santunu Kaysar'
    audio_url = request.POST.get('audio_url', '').strip() or None
    cover_url = request.POST.get('cover_url', '').strip() or None
    genre = request.POST.get('genre', '').strip() or 'Lo-Fi / Ambient'
    duration = request.POST.get('duration', '').strip() or '3:20'
    is_favorite = request.POST.get('is_favorite') in ('1', 'true', 'on', True)

    audio_file = request.FILES.get('audio_file')
    cover_image = request.FILES.get('cover_image')

    if not audio_file and not audio_url:
        return JsonResponse({'success': False, 'error': 'Please provide either an audio file or an audio URL.'}, status=400)

    board = None
    board_id = request.POST.get('board_id')
    if board_id:
        board = PinBoard.objects.filter(pk=board_id).first()

    track = PinAudioTrack.objects.create(
        title=title,
        artist=artist,
        audio_file=audio_file,
        audio_url=audio_url,
        cover_image=cover_image,
        cover_url=cover_url,
        genre=genre,
        duration=duration,
        is_favorite=is_favorite,
        board=board
    )

    return JsonResponse({
        'success': True,
        'message': f"Added '{track.title}' to your music collection!",
        'track': track.to_dict(),
        'favorite_count': PinAudioTrack.objects.filter(is_favorite=True).count()
    })


@require_http_methods(["POST", "DELETE"])
def api_delete_music_track(request, track_id):
    """Delete a music track (strictly requires administrator / staff permission)."""
    user = getattr(request, 'user', None)
    if not (user and user.is_authenticated and (user.is_staff or user.is_superuser)):
        return JsonResponse({
            'success': False,
            'error': 'Admin authorization required. Only portfolio administrators can delete music tracks.',
            'requires_admin': True,
            'login_url': '/admin/login/?next=/pin-interast/'
        }, status=403)

    track = get_object_or_404(PinAudioTrack, pk=track_id)
    title = track.title
    track.delete()
    return JsonResponse({
        'success': True,
        'message': f"Deleted '{title}' from library.",
        'favorite_count': PinAudioTrack.objects.filter(is_favorite=True).count()
    })

