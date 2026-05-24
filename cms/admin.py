from django.contrib import admin

from .models import (
    ContactMessage,
    EventCategory,
    EventGalleryImage,
    Host,
    SiteGalleryImage,
    SiteSettings,
    SocialLink,
    Testimonial,
    WorkshopEvent,
)


class EventGalleryImageInline(admin.TabularInline):
    model = EventGalleryImage
    extra = 1


@admin.register(WorkshopEvent)
class WorkshopEventAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "category", "is_published", "is_featured", "sort_order")
    list_filter = ("is_published", "is_featured", "category")
    search_fields = ("title", "slug", "venue")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [EventGalleryImageInline]


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    search_fields = ("name", "role")


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")


@admin.register(SiteGalleryImage)
class SiteGalleryImageAdmin(admin.ModelAdmin):
    list_display = ("alt", "sort_order", "is_published")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "sort_order")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "platform", "is_published", "sort_order")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_read", "created_at")
    list_filter = ("is_read",)
    readonly_fields = ("created_at",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
