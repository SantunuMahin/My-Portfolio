from html import escape
from urllib.parse import urljoin

from django.conf import settings as django_settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ContactMessage, Profile


def _smtp_ready(settings_obj):
    host_user = getattr(settings_obj, 'EMAIL_HOST_USER', '')
    host_pass = getattr(settings_obj, 'EMAIL_HOST_PASSWORD', '')
    return (
        host_user and host_pass
        and 'your_gmail' not in host_user
        and 'your_app_password' not in host_pass
    )


def _html(value):
    return escape(str(value or ''), quote=True)


def _html_block(value):
    return _html(value).replace('\n', '<br>')


def _absolute_url(path, base_url=None):
    if not path:
        return ''
    if path.startswith(('http://', 'https://')):
        return path
    if base_url:
        return urljoin(base_url, path)
    return path


def _profile_avatar_url(profile, base_url=None, default="https://i.postimg.cc/XNw7StsF/santunu.jpg"):
    return default


def _avatar_html(owner_name, avatar_url):
    safe_name = _html(owner_name)
    if avatar_url:
        return (
            f'<img src="{_html(avatar_url)}" alt="{safe_name}" width="64" height="64" '
            'style="display:block;width:64px;height:64px;border-radius:18%;object-fit:cover;'
            'border:2px solid rgba(77,218,251,0.45);box-shadow:0 10px 28px rgba(77,218,251,0.18);">'
        )

    initial = _html((owner_name or 'S')[0].upper())
    return (
        '<div style="width:64px;height:64px;border-radius:18%;'
        'background:linear-gradient(135deg,#22d3ee,#c084fc);'
        'font-size:24px;font-weight:800;color:#ffffff;text-align:center;line-height:64px;'
        'font-family:Space Grotesk,Segoe UI,Arial,sans-serif;box-shadow:0 10px 28px rgba(77,218,251,0.18);">'
        f'{initial}</div>'
    )


def _link_button(label, href, primary=False):
    if not href:
        return ''
    bg = 'rgba(77,218,251,0.14)' if primary else 'rgba(255,255,255,0.05)'
    border = 'rgba(77,218,251,0.34)' if primary else 'rgba(255,255,255,0.10)'
    color = '#67e8f9' if primary else '#cbd5e1'
    return (
        '<a href="{href}" style="display:inline-block;margin:0 6px 8px 0;padding:8px 14px;'
        'background:{bg};border:1px solid {border};border-radius:999px;color:{color};'
        'text-decoration:none;font-size:12px;font-weight:700;font-family:Poppins,Segoe UI,Arial,sans-serif;">'
        '{label}</a>'
    ).format(href=_html(href), bg=bg, border=border, color=color, label=_html(label))


def _signature_html(profile, owner_name, base_url=None, note='I look forward to speaking with you.'):
    owner_title = profile.title if profile and profile.title else 'Full Stack Developer'
    owner_bio = ''
    if profile and profile.bio:
        owner_bio = profile.bio[:180] + '...' if len(profile.bio) > 180 else profile.bio

    avatar_url = _profile_avatar_url(profile, base_url)
    portfolio_url = _absolute_url('/', base_url) or 'http://127.0.0.1:8000/'
    blog_url = _absolute_url('/blog/', base_url) or 'http://127.0.0.1:8000/blog/'
    books_url = _absolute_url('/books/', base_url) or 'http://127.0.0.1:8000/books/'
    pins_url = _absolute_url('/pins/', base_url) or 'http://127.0.0.1:8000/pins/'
    github_url = profile.github_url if profile and profile.github_url else ''
    linkedin_url = profile.linkedin_url if profile and profile.linkedin_url else ''

    bio_html = ''
    if owner_bio:
        bio_html = (
            '<p style="margin:10px 0 0;font-size:13px;color:#94a3b8;line-height:1.65;">'
            f'{_html(owner_bio)}</p>'
        )

    social_buttons = [
        _link_button('Portfolio', portfolio_url, True),
        _link_button('Blog', blog_url),
        _link_button('Books', books_url),
        _link_button('Pinterest', pins_url),
    ]
    if profile:
        for s in profile.get_social_links():
            if s.get('url'):
                social_buttons.append(_link_button(s.get('label', 'Link'), s['url']))
    social_buttons_html = '\n        '.join(social_buttons)

    return f"""
  <tr>
    <td style="background:linear-gradient(135deg,rgba(34,211,238,0.12),rgba(192,132,252,0.10));
               border:1px solid rgba(148,163,184,0.14);border-top:none;
               padding:26px 32px;border-radius:0 0 16px 16px;">
      <table cellpadding="0" cellspacing="0" width="100%">
        <tr>
          <td style="width:80px;padding-right:18px;vertical-align:top;">
            {_avatar_html(owner_name, avatar_url)}
          </td>
          <td style="vertical-align:top;">
            <p style="margin:0;font-size:17px;font-weight:800;color:#f8fafc;font-family:Space Grotesk,Segoe UI,Arial,sans-serif;">
              {_html(owner_name)}
            </p>
            <p style="margin:4px 0 0;font-size:13px;color:#67e8f9;font-weight:700;">{_html(owner_title)}</p>
            <p style="margin:9px 0 0;font-size:13px;color:#94a3b8;line-height:1.6;">{_html(note)}</p>
            {bio_html}
          </td>
        </tr>
      </table>
      <div style="margin-top:20px;">
        {social_buttons_html}
      </div>
    </td>
  </tr>
"""


def _email_shell(pretitle, heading, body_html, quote_html, signature_html, footer_text):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_html(heading)}</title>
</head>
<body style="margin:0;padding:0;background:#020617;font-family:Poppins,Segoe UI,Arial,sans-serif;color:#cbd5e1;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#020617;padding:34px 16px;">
<tr>
<td align="center">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;border-collapse:separate;border-spacing:0;">
  <tr>
    <td style="height:4px;background:linear-gradient(135deg,#22d3ee,#c084fc);border-radius:16px 16px 0 0;"></td>
  </tr>
  <tr>
    <td style="background:linear-gradient(135deg,rgba(15,23,42,0.98),rgba(30,41,59,0.94));
               border:1px solid rgba(148,163,184,0.16);border-top:none;padding:30px 32px 22px;">
      <p style="margin:0;font-size:12px;letter-spacing:1.8px;text-transform:uppercase;color:#67e8f9;font-weight:800;">
        {_html(pretitle)}
      </p>
      <h1 style="margin:9px 0 0;font-size:24px;line-height:1.28;color:#f8fafc;font-family:Space Grotesk,Segoe UI,Arial,sans-serif;">
        {_html(heading)}
      </h1>
    </td>
  </tr>
  <tr>
    <td style="background:rgba(15,23,42,0.96);border:1px solid rgba(148,163,184,0.14);
               border-top:none;padding:28px 32px;">
      {body_html}
    </td>
  </tr>
  {quote_html}
  {signature_html}
  <tr>
    <td style="padding:16px 8px 0;text-align:center;">
      <p style="margin:0;font-size:12px;color:#475569;">{_html(footer_text)}</p>
    </td>
  </tr>
</table>
</td>
</tr>
</table>
</body>
</html>"""


@require_POST
def contact_view(request):
    """Handle contact form: save to DB always, try SMTP if configured."""
    # Honeypot field check to thwart automated spam bots silently
    honeypot = request.POST.get('hp_company', '').strip()
    if honeypot:
        return JsonResponse({'ok': True, 'message': "Thanks for reaching out! Your message was received."})

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    subject = request.POST.get('subject', '').strip() or 'No Subject'
    message = request.POST.get('message', '').strip()

    if not name or not email or not message:
        return JsonResponse({'ok': False, 'error': 'Please fill in all required fields.'}, status=400)

    msg_obj = ContactMessage.objects.create(
        name=name,
        email=email,
        subject=subject,
        message=message,
    )

    host_user = getattr(django_settings, 'EMAIL_HOST_USER', '')
    recipient = getattr(django_settings, 'CONTACT_RECIPIENT_EMAIL', '') or host_user

    if _smtp_ready(django_settings) and recipient:
        profile = Profile.objects.first()
        owner_name = profile.name if profile and profile.name else 'Santunu Kaysar'
        base_url = request.build_absolute_uri('/')

        owner_message = (
            "New message from your portfolio contact form\n"
            f"{'=' * 48}\n\n"
            f"Name    : {name}\n"
            f"Email   : {email}\n"
            f"Subject : {subject}\n\n"
            f"Message:\n{message}\n"
        )

        visitor_message = (
            f"Hi {name},\n\n"
            "Thank you for getting in touch! This is an automatic confirmation to let you know "
            "I have successfully received your message through my portfolio website.\n\n"
            "Here is a copy of your submission:\n"
            f"{'-' * 48}\n"
            f"Subject: {subject}\n"
            f"Message:\n{message}\n"
            f"{'-' * 48}\n\n"
            "I will review your message and get back to you as soon as possible.\n\n"
            "Best regards,\n"
            f"{owner_name}"
        )

        body_html = (
            '<p style="margin:0;font-size:15px;line-height:1.8;color:#cbd5e1;">'
            f'Hi {_html(name)},<br><br>'
            "Thanks for getting in touch. This is a quick note to confirm that I received your "
            "message through my portfolio, and I will review it as soon as possible."
            '</p>'
        )
        quote_html = f"""
  <tr>
    <td style="background:rgba(2,6,23,0.96);border:1px solid rgba(148,163,184,0.12);
               border-top:none;border-left:3px solid rgba(103,232,249,0.55);padding:22px 32px;">
      <p style="margin:0 0 12px;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#64748b;font-weight:800;">
        Your Submission
      </p>
      <p style="margin:0 0 10px;font-size:13px;color:#94a3b8;">
        Subject: <span style="color:#cbd5e1;">{_html(subject or '(no subject)')}</span>
      </p>
      <div style="font-size:13px;color:#94a3b8;line-height:1.7;border-left:2px solid rgba(148,163,184,0.18);padding-left:14px;">
        {_html_block(message)}
      </div>
    </td>
  </tr>
"""
        visitor_html = _email_shell(
            pretitle='Confirmation Mail',
            heading='Thank you for reaching out!',
            body_html=body_html,
            quote_html=quote_html,
            signature_html=_signature_html(profile, owner_name, base_url),
            footer_text=f"This confirmation was sent from {owner_name}'s portfolio contact system.",
        )

        try:
            send_mail(
                subject=f"[Portfolio Contact] {subject}",
                message=owner_message,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            msg_obj.email_sent = True
            msg_obj.save(update_fields=['email_sent'])
        except Exception as exc:
            print(f"SMTP ERROR (Site Owner Notification): {exc}")
            import traceback
            traceback.print_exc()

        try:
            email_msg = EmailMultiAlternatives(
                subject=f"Thank you for reaching out! - {owner_name}",
                body=visitor_message,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            email_msg.attach_alternative(visitor_html, 'text/html')
            email_msg.send(fail_silently=False)
        except Exception as exc:
            print(f"SMTP ERROR (Visitor Auto-reply): {exc}")
            import traceback
            traceback.print_exc()

    return JsonResponse({
        'ok': True,
        'message': "Thanks for reaching out! I've received your message and will get back to you soon.",
    })


def send_reply(contact_msg, reply_text, owner_name=None, base_url=None):
    """
    Send a direct reply email to a contact message sender.
    Sends rich HTML email with branded signature.
    Returns (success: bool, error_message: str)
    """
    from django.conf import settings as s

    profile = Profile.objects.first()
    if not owner_name:
        owner_name = profile.name if profile and profile.name else 'Santunu Kaysar'

    if not _smtp_ready(s):
        return False, 'SMTP is not configured. Fill in EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env'

    subject = f"Re: {contact_msg.subject}" if contact_msg.subject else f"Reply from {owner_name}"
    portfolio_url = _absolute_url('/', base_url) or 'http://127.0.0.1:8000/'
    blog_url = _absolute_url('/blog/', base_url) or 'http://127.0.0.1:8000/blog/'
    books_url = _absolute_url('/books/', base_url) or 'http://127.0.0.1:8000/books/'
    pins_url = _absolute_url('/pins/', base_url) or 'http://127.0.0.1:8000/pins/'

    plain_text = (
        f"Hi {contact_msg.name},\n\n"
        f"{reply_text}\n\n"
        f"- {owner_name}\n"
        f"{'-' * 40}\n"
        f"Portfolio : {portfolio_url}\n"
        f"Blog      : {blog_url}\n"
        f"Books     : {books_url}\n"
        f"Pinterest : {pins_url}\n\n"
        "- Original Message -\n"
        f"Subject : {contact_msg.subject}\n"
        f"Message : {contact_msg.message}\n"
    )

    body_html = (
        '<p style="margin:0 0 8px;font-size:13px;color:#94a3b8;">'
        f'Hi {_html(contact_msg.name)},</p>'
        '<div style="font-size:15px;line-height:1.85;color:#cbd5e1;">'
        f'{_html_block(reply_text)}</div>'
    )
    quote_html = f"""
  <tr>
    <td style="background:rgba(2,6,23,0.96);border:1px solid rgba(148,163,184,0.12);
               border-top:none;border-left:3px solid rgba(103,232,249,0.55);padding:22px 32px;">
      <p style="margin:0 0 12px;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#64748b;font-weight:800;">
        Original Message
      </p>
      <p style="margin:0 0 5px;font-size:13px;color:#94a3b8;">
        From: <span style="color:#cbd5e1;">{_html(contact_msg.name)} &lt;{_html(contact_msg.email)}&gt;</span>
      </p>
      <p style="margin:0 0 10px;font-size:13px;color:#94a3b8;">
        Subject: <span style="color:#cbd5e1;">{_html(contact_msg.subject or '(no subject)')}</span>
      </p>
      <div style="font-size:13px;color:#94a3b8;line-height:1.7;border-left:2px solid rgba(148,163,184,0.18);padding-left:14px;">
        {_html_block(contact_msg.message)}
      </div>
    </td>
  </tr>
"""
    html_body = _email_shell(
        pretitle='Personal Reply',
        heading=f"Re: {contact_msg.subject or 'Your Message'}",
        body_html=body_html,
        quote_html=quote_html,
        signature_html=_signature_html(profile, owner_name, base_url),
        footer_text=f"This is a personal reply from {owner_name}'s portfolio contact system.",
    )

    try:
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=s.DEFAULT_FROM_EMAIL,
            to=[contact_msg.email],
        )
        email_msg.attach_alternative(html_body, 'text/html')
        email_msg.send(fail_silently=False)
        return True, ''
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return False, str(exc)
