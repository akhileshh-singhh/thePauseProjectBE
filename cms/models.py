from django.db import models


class EventCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "event categories"

    def __str__(self) -> str:
        return self.name


class Host(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    bio = models.TextField()
    image = models.URLField(max_length=500)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class WorkshopEvent(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    event_date = models.DateField(help_text="Workshop calendar date")
    start_time = models.TimeField(help_text="Session start time")
    end_time = models.TimeField(null=True, blank=True, help_text="Session end time")
    venue = models.CharField(max_length=255)
    price_display = models.CharField(max_length=32)
    image = models.URLField(max_length=500)
    booking_link = models.URLField(max_length=500)
    short_description = models.TextField()
    description = models.TextField()
    category = models.ForeignKey(
        EventCategory, on_delete=models.PROTECT, related_name="events"
    )
    host = models.ForeignKey(Host, on_delete=models.PROTECT, related_name="events")
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.title


class EventGalleryImage(models.Model):
    event = models.ForeignKey(
        WorkshopEvent, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image_url = models.URLField(max_length=500)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.event.slug} #{self.sort_order}"


class SiteGalleryImage(models.Model):
    src = models.URLField(max_length=500)
    alt = models.CharField(max_length=255)
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.alt


class Testimonial(models.Model):
    quote = models.TextField()
    name = models.CharField(max_length=120)
    context = models.CharField(max_length=200)
    event = models.ForeignKey(
        WorkshopEvent,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="testimonials",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.name


class SocialLink(models.Model):
    class Platform(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        LINKTREE = "linktree", "Linktree"
        WHATSAPP = "whatsapp", "WhatsApp"
        OTHER = "other", "Other"

    platform = models.CharField(max_length=32, choices=Platform.choices)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    href = models.URLField(max_length=500)
    cta_label = models.CharField(max_length=64, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title


class SiteSettings(models.Model):
    """Singleton site-wide copy and SEO defaults."""

    site_name = models.CharField(max_length=120, default="The Pause Project")
    metadata_base_url = models.URLField(
        max_length=500, blank=True, default="https://thepauseproject.in"
    )
    default_meta_description = models.TextField(blank=True)

    hero_eyebrow = models.CharField(max_length=120, blank=True)
    hero_title = models.CharField(max_length=200, blank=True)
    hero_subtitle = models.TextField(blank=True)
    hero_cta_primary_label = models.CharField(max_length=64, blank=True)
    hero_cta_primary_href = models.CharField(max_length=200, blank=True)
    hero_cta_secondary_label = models.CharField(max_length=64, blank=True)
    hero_cta_secondary_href = models.CharField(max_length=200, blank=True)

    about_heading = models.CharField(max_length=200, blank=True)
    about_body = models.TextField(blank=True)
    about_sidebar_heading = models.CharField(max_length=200, blank=True)
    about_sidebar_body = models.TextField(blank=True)

    events_section_label = models.CharField(max_length=64, blank=True)
    events_section_heading = models.CharField(max_length=200, blank=True)
    events_section_body = models.TextField(blank=True)

    gallery_section_label = models.CharField(max_length=64, blank=True)
    gallery_section_heading = models.CharField(max_length=200, blank=True)
    gallery_section_body = models.TextField(blank=True)

    testimonials_section_label = models.CharField(max_length=64, blank=True)
    testimonials_section_heading = models.CharField(max_length=200, blank=True)

    contact_heading = models.CharField(max_length=200, blank=True)
    contact_body = models.TextField(blank=True)
    contact_address = models.TextField(blank=True)
    contact_whatsapp_url = models.URLField(max_length=500, blank=True)

    footer_tagline = models.CharField(max_length=255, blank=True)
    instagram_url = models.URLField(max_length=500, blank=True)

    class Meta:
        verbose_name_plural = "site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return "Site settings"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} · {self.created_at:%Y-%m-%d}"
