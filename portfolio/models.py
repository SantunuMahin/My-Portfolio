from django.db import models


class ContactMessage(models.Model):
    """Stores contact form submissions. Always saved; email is optional."""
    name       = models.CharField(max_length=200)
    email      = models.EmailField()
    subject    = models.CharField(max_length=300, blank=True)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False, help_text="Mark as read in admin")
    email_sent = models.BooleanField(default=False, help_text="Was notification email delivered?")
    sent_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"From {self.name} <{self.email}> — {self.sent_at:%Y-%m-%d %H:%M}"


class Profile(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200, help_text="e.g. Full Stack Django Developer")
    bio = models.TextField()
    email = models.EmailField()
    location = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    company_url = models.URLField(blank=True)
    university = models.CharField(max_length=200, blank=True)
    university_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True, help_text="Facebook profile or page URL")
    pinterest_url = models.URLField(blank=True, help_text="Pinterest profile URL")
    twitter_url = models.URLField(blank=True, help_text="Twitter / X profile URL")
    instagram_url = models.URLField(blank=True, help_text="Instagram profile URL")
    youtube_url = models.URLField(blank=True, help_text="YouTube channel or video URL")
    daizzy_url = models.URLField(blank=True, help_text="Daizzy external link URL")
    avatar = models.ImageField(upload_to='profile/', blank=True, null=True)
    cv = models.FileField(upload_to='cv/', blank=True, null=True, help_text="Upload your CV (PDF)")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.name

    def get_social_links(self):
        """Returns unified dynamic list of all configured social links."""
        links = []
        # Explicitly configured SocialLink objects
        custom_links = list(self.social_links.filter(is_active=True).order_by('order', 'id'))
        for cl in custom_links:
            links.append({
                'platform': cl.platform,
                'label': cl.label or cl.get_platform_display(),
                'url': cl.url,
                'icon': cl.get_icon(),
            })

        # Synthesize from profile direct fields if not already added
        existing_urls = {l['url'] for l in links}
        field_map = [
            ('github', 'GitHub', self.github_url, 'logo-github'),
            ('linkedin', 'LinkedIn', self.linkedin_url, 'logo-linkedin'),
            ('facebook', 'Facebook', self.facebook_url, 'logo-facebook'),
            ('pinterest', 'Pinterest', self.pinterest_url, 'logo-pinterest'),
            ('twitter', 'Twitter / X', self.twitter_url, 'logo-twitter'),
            ('instagram', 'Instagram', self.instagram_url, 'logo-instagram'),
            ('youtube', 'YouTube', self.youtube_url, 'logo-youtube'),
        ]
        for platform, label, url, icon in field_map:
            if url and url not in existing_urls:
                links.append({
                    'platform': platform,
                    'label': label,
                    'url': url,
                    'icon': icon,
                })
                existing_urls.add(url)
        return links


class SocialLink(models.Model):
    """Dynamic custom social or external links for the profile."""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('pinterest', 'Pinterest'),
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter / X'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('discord', 'Discord'),
        ('telegram', 'Telegram'),
        ('kaggle', 'Kaggle'),
        ('leetcode', 'LeetCode'),
        ('dribbble', 'Dribbble'),
        ('behance', 'Behance'),
        ('medium', 'Medium'),
        ('whatsapp', 'WhatsApp'),
        ('custom', 'Custom / Website'),
    ]
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='social_links',
        null=True, blank=True, help_text="Link to profile"
    )
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='facebook')
    label = models.CharField(max_length=100, blank=True, help_text="Display label (e.g. 'Facebook Page', 'Pinterest Art')")
    url = models.URLField(help_text="Full link URL")
    icon_name = models.CharField(
        max_length=60, blank=True,
        help_text="Custom Ionicon name (leave blank to auto-detect from platform choice)"
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"

    def __str__(self):
        return f"{self.label or self.get_platform_display()} ({self.url})"

    def get_icon(self):
        if self.icon_name:
            return self.icon_name
        defaults = {
            'facebook': 'logo-facebook',
            'pinterest': 'logo-pinterest',
            'github': 'logo-github',
            'linkedin': 'logo-linkedin',
            'twitter': 'logo-twitter',
            'instagram': 'logo-instagram',
            'youtube': 'logo-youtube',
            'discord': 'logo-discord',
            'telegram': 'paper-plane-outline',
            'kaggle': 'analytics-outline',
            'leetcode': 'code-slash-outline',
            'dribbble': 'logo-dribbble',
            'behance': 'logo-behance',
            'medium': 'logo-medium',
            'whatsapp': 'logo-whatsapp',
            'custom': 'globe-outline',
        }
        return defaults.get(self.platform, 'link-outline')


class Experience(models.Model):
    company = models.CharField(max_length=200)
    company_url = models.URLField(blank=True)
    role = models.CharField(max_length=200)
    start_date = models.CharField(max_length=50, help_text="e.g. January 2023")
    end_date = models.CharField(max_length=50, blank=True, help_text="Leave blank if current")
    is_current = models.BooleanField(default=False)
    description = models.TextField(help_text="Bullet points, one per line")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"

    def __str__(self):
        return f"{self.role} at {self.company}"

    def get_bullets(self):
        return [b.strip() for b in self.description.splitlines() if b.strip()]

    def get_period(self):
        if self.is_current:
            return f"{self.start_date} — Present"
        return f"{self.start_date} — {self.end_date}"


class Education(models.Model):
    institution = models.CharField(max_length=200)
    institution_url = models.URLField(blank=True)
    degree = models.CharField(max_length=200)
    field = models.CharField(max_length=200, blank=True)
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True, help_text="Additional info, one bullet per line")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = "Education"
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree} — {self.institution}"

    def get_bullets(self):
        return [b.strip() for b in self.details.splitlines() if b.strip()]

    def get_period(self):
        if self.end_date:
            return f"{self.start_date} — {self.end_date}"
        return self.start_date


class SkillCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='skills/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    level = models.PositiveIntegerField(default=80, help_text="Proficiency 0-100")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.category})"


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('ml', 'Machine Learning'),
        ('mobile', 'Mobile App'),
        ('data', 'Data Science'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='web')
    description = models.TextField()
    tech_stack = models.CharField(max_length=300, blank=True, help_text="e.g. Django, React, PostgreSQL")
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def get_tech_list(self):
        return [t.strip() for t in self.tech_stack.split(',') if t.strip()]


class Service(models.Model):
    """What I do / Areas of expertise shown on About page."""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='services/', blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, help_text="Ionicon name e.g. code-slash-outline")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Certificate(models.Model):
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    date = models.CharField(max_length=50, help_text="e.g. May 2024")
    url = models.URLField(blank=True)
    description = models.TextField(blank=True, help_text="Optional description")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    def __str__(self):
        return f"{self.title} — {self.issuer}"


class CustomNavLink(models.Model):
    """Dynamic custom navigation links in the navbar (e.g. Daizzy, Docs, external tools)."""
    title = models.CharField(max_length=60, help_text="Link title (e.g. Daizzy)")
    url = models.URLField(help_text="Target external or internal URL")
    icon_name = models.CharField(
        max_length=60, blank=True,
        help_text="Ionicon name e.g. sparkles-outline, globe-outline, open-outline, rocket-outline"
    )
    open_in_new_tab = models.BooleanField(default=True, help_text="Open in a new browser tab")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Custom Nav Link"
        verbose_name_plural = "Custom Nav Links"

    def __str__(self):
        return f"{self.title} ({self.url})"

    def get_icon(self):
        return self.icon_name or 'open-outline'
