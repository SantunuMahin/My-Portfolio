from django.contrib import admin
from .models import (
    Profile, Experience, Education, SkillCategory, Skill,
    Project, Service, ContactMessage, Certificate, SocialLink, CustomNavLink
)


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 2
    fields = ['platform', 'label', 'url', 'icon_name', 'order', 'is_active']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'email']
    inlines = [SocialLinkInline]
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'title', 'bio', 'email', 'avatar', 'cv']
        }),
        ('Work & Education Links', {
            'fields': ['company', 'company_url', 'university', 'university_url', 'location']
        }),
        ('Social & External Links', {
            'fields': ['daizzy_url', 'github_url', 'linkedin_url', 'facebook_url', 'pinterest_url', 'twitter_url', 'instagram_url', 'youtube_url'],
            'classes': ['collapse'],
            'description': 'Direct URLs for standard platforms and Daizzy. You can also add unlimited custom nav links or social profiles below.'
        }),
    ]


@admin.register(CustomNavLink)
class CustomNavLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'icon_name', 'open_in_new_tab', 'order', 'is_active']
    list_editable = ['order', 'is_active', 'open_in_new_tab']
    list_filter = ['is_active', 'open_in_new_tab']
    search_fields = ['title', 'url']


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['label_display', 'platform', 'url', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['platform', 'is_active']
    search_fields = ['label', 'url']

    @admin.display(description='Label')
    def label_display(self, obj):
        return obj.label or obj.get_platform_display()


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['role', 'company', 'start_date', 'is_current', 'order']
    list_editable = ['order', 'is_current']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'start_date', 'end_date', 'order']
    list_editable = ['order']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['title', 'issuer', 'date', 'order']
    list_editable = ['order']


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']
    inlines = [SkillInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'order']
    list_editable = ['is_featured', 'order']
    list_filter = ['category', 'is_featured']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ['name', 'email', 'subject', 'sent_at', 'is_read', 'email_sent', 'reply_link']
    list_filter   = ['is_read', 'email_sent', 'sent_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'sent_at', 'email_sent']
    list_editable = ['is_read']
    ordering      = ['-sent_at']
    actions       = ['mark_as_read']

    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.display(description='Reply')
    def reply_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        url = reverse('admin:portfolio_contactmessage_reply', args=[obj.pk])
        return format_html('<a href="{}" style="color:#4dabf7;font-weight:600;">Reply</a>', url)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('<int:pk>/reply/', self.admin_site.admin_view(self.reply_view),
                 name='portfolio_contactmessage_reply'),
        ]
        return custom + urls

    def reply_view(self, request, pk):
        from django.shortcuts import get_object_or_404, redirect, render
        from django.contrib import messages as admin_messages
        from .smtpmail import send_reply

        msg = get_object_or_404(ContactMessage, pk=pk)

        if request.method == 'POST':
            reply_text = request.POST.get('reply_text', '').strip()
            if not reply_text:
                admin_messages.error(request, 'Reply text cannot be empty.')
            else:
                ok, err = send_reply(msg, reply_text, base_url=request.build_absolute_uri('/'))
                if ok:
                    msg.is_read = True
                    msg.save(update_fields=['is_read'])
                    admin_messages.success(request, f'Reply sent to {msg.email} successfully!')
                    return redirect('admin:portfolio_contactmessage_changelist')
                else:
                    admin_messages.error(request, f'Failed to send reply: {err}')

        context = {
            **self.admin_site.each_context(request),
            'msg': msg,
            'profile': Profile.objects.first(),
            'title': f'Reply to {msg.name}',
            'opts': self.model._meta,
        }
        return render(request, 'admin/portfolio/contactmessage/reply.html', context)
