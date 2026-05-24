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


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ["id", "name", "role", "bio", "image"]


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "sort_order"]


class EventGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGalleryImage
        fields = ["id", "image_url", "sort_order"]


class WorkshopEventPublicSerializer(serializers.ModelSerializer):
    """Matches the Next.js WorkshopEvent type."""

    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    price = serializers.CharField(source="price_display")
    bookingLink = serializers.CharField(source="booking_link")
    shortDescription = serializers.CharField(source="short_description")
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

    def get_gallery(self, obj: WorkshopEvent) -> list[str]:
        return list(
            obj.gallery_images.order_by("sort_order", "id").values_list(
                "image_url", flat=True
            )
        )


class WorkshopEventAdminSerializer(serializers.ModelSerializer):
    gallery = EventGalleryImageSerializer(
        source="gallery_images", many=True, required=False
    )
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

    def _save_gallery(self, event: WorkshopEvent, gallery_data: list | None) -> None:
        if gallery_data is None:
            return
        event.gallery_images.all().delete()
        for index, item in enumerate(gallery_data):
            EventGalleryImage.objects.create(
                event=event,
                image_url=item["image_url"],
                sort_order=item.get("sort_order", index),
            )

    def create(self, validated_data: dict) -> WorkshopEvent:
        gallery_data = validated_data.pop("gallery_images", None)
        event = WorkshopEvent.objects.create(**validated_data)
        self._save_gallery(event, gallery_data)
        return event

    def update(self, instance: WorkshopEvent, validated_data: dict) -> WorkshopEvent:
        gallery_data = validated_data.pop("gallery_images", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._save_gallery(instance, gallery_data)
        return instance


class SiteGalleryPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteGalleryImage
        fields = ["src", "alt", "caption"]


class SiteGalleryAdminSerializer(serializers.ModelSerializer):
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
