from rest_framework import serializers

from .event_format import format_event_date, format_event_time
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
from .utils import absolute_media_url


class AbsoluteImageField(serializers.ImageField):
    def to_representation(self, value):
        return absolute_media_url(self.context.get("request"), value)


class HostSerializer(serializers.ModelSerializer):
    image = AbsoluteImageField(required=False, allow_null=True)

    class Meta:
        model = Host
        fields = ["id", "name", "role", "bio", "image"]


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "sort_order"]


class EventGalleryImageSerializer(serializers.ModelSerializer):
    image = AbsoluteImageField()

    class Meta:
        model = EventGalleryImage
        fields = ["id", "image", "sort_order"]


class WorkshopEventPublicSerializer(serializers.ModelSerializer):
    """Matches the Next.js WorkshopEvent type."""

    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    price = serializers.CharField(source="price_display")
    bookingLink = serializers.CharField(source="booking_link")
    shortDescription = serializers.CharField(source="short_description")
    image = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    host = HostSerializer(read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = WorkshopEvent
        fields = [
            "title",
            "slug",
            "date",
            "time",
            "venue",
            "price",
            "image",
            "bookingLink",
            "shortDescription",
            "description",
            "gallery",
            "host",
            "category",
        ]

    def get_date(self, obj: WorkshopEvent) -> str:
        return format_event_date(obj.event_date)

    def get_time(self, obj: WorkshopEvent) -> str:
        return format_event_time(obj.start_time, obj.end_time)

    def get_image(self, obj: WorkshopEvent) -> str:
        return absolute_media_url(self.context.get("request"), obj.image)

    def get_gallery(self, obj: WorkshopEvent) -> list[str]:
        request = self.context.get("request")
        return [
            absolute_media_url(request, row.image)
            for row in obj.gallery_images.order_by("sort_order", "id")
        ]


class WorkshopEventAdminSerializer(serializers.ModelSerializer):
    gallery = EventGalleryImageSerializer(
        source="gallery_images", many=True, read_only=True
    )
    image = AbsoluteImageField(required=False, allow_null=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = WorkshopEvent
        fields = [
            "id",
            "title",
            "slug",
            "event_date",
            "start_time",
            "end_time",
            "venue",
            "price_display",
            "image",
            "booking_link",
            "short_description",
            "description",
            "category",
            "category_name",
            "host",
            "is_published",
            "is_featured",
            "sort_order",
            "gallery",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def _gallery_files(self) -> list:
        request = self.context.get("request")
        if request is None:
            return []
        return request.FILES.getlist("gallery")

    def _save_gallery(self, event: WorkshopEvent, replace: bool) -> None:
        gallery_files = self._gallery_files()
        if not replace:
            return
        event.gallery_images.all().delete()
        for index, uploaded in enumerate(gallery_files):
            EventGalleryImage.objects.create(
                event=event,
                image=uploaded,
                sort_order=index,
            )

    def create(self, validated_data: dict) -> WorkshopEvent:
        replace_gallery = bool(self._gallery_files())
        event = WorkshopEvent.objects.create(**validated_data)
        self._save_gallery(event, replace_gallery)
        return event

    def update(self, instance: WorkshopEvent, validated_data: dict) -> WorkshopEvent:
        replace_gallery = bool(self._gallery_files())
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._save_gallery(instance, replace_gallery)
        return instance


class SiteGalleryPublicSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = SiteGalleryImage
        fields = ["src", "alt", "caption"]

    def get_src(self, obj: SiteGalleryImage) -> str:
        return absolute_media_url(self.context.get("request"), obj.src)


class SiteGalleryAdminSerializer(serializers.ModelSerializer):
    src = AbsoluteImageField(required=False, allow_null=True)

    class Meta:
        model = SiteGalleryImage
        fields = [
            "id",
            "src",
            "alt",
            "caption",
            "sort_order",
            "is_published",
        ]


class TestimonialPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["quote", "name", "context"]


class TestimonialAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "id",
            "quote",
            "name",
            "context",
            "event",
            "sort_order",
            "is_published",
        ]


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = [
            "id",
            "platform",
            "title",
            "description",
            "href",
            "cta_label",
            "sort_order",
            "is_published",
        ]


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "site_name",
            "metadata_base_url",
            "default_meta_description",
            "hero_eyebrow",
            "hero_title",
            "hero_subtitle",
            "hero_cta_primary_label",
            "hero_cta_primary_href",
            "hero_cta_secondary_label",
            "hero_cta_secondary_href",
            "about_heading",
            "about_body",
            "about_sidebar_heading",
            "about_sidebar_body",
            "events_section_label",
            "events_section_heading",
            "events_section_body",
            "gallery_section_label",
            "gallery_section_heading",
            "gallery_section_body",
            "testimonials_section_label",
            "testimonials_section_heading",
            "contact_heading",
            "contact_body",
            "contact_address",
            "contact_whatsapp_url",
            "footer_tagline",
            "instagram_url",
        ]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "message", "is_read", "created_at"]
        read_only_fields = ["is_read", "created_at"]


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
