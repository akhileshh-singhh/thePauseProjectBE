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
    image = serializers.SerializerMethodField()
    image_file = serializers.ImageField(source="image", write_only=True, required=False)

    class Meta:
        model = Host
        fields = ["id", "name", "role", "bio", "image", "image_file"]

    def get_image(self, obj) -> str | None:
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "sort_order"]


class EventGalleryImageSerializer(serializers.ModelSerializer):
    # ✅ Resolve to absolute asset string URLs
    image_url = serializers.SerializerMethodField()
    image_file = serializers.ImageField(source="image_url", write_only=True, required=False)

    class Meta:
        model = EventGalleryImage
        fields = ["id", "image_url", "image_file", "sort_order"]

    def get_image_url(self, obj) -> str | None:
        if obj.image_url:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image_url.url) if request else obj.image_url.url
        return None


class WorkshopEventPublicSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    price = serializers.CharField(source="price_display")
    bookingLink = serializers.CharField(source="booking_link")
    shortDescription = serializers.CharField(source="short_description")
    gallery = serializers.SerializerMethodField()
    host = HostSerializer(read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    # ✅ Resolve main image to absolute string URL
    image = serializers.SerializerMethodField()

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

    def get_image(self, obj) -> str | None:
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_date(self, obj: WorkshopEvent) -> str:
        return format_event_date(obj.event_date)

    def get_time(self, obj: WorkshopEvent) -> str:
        return format_event_time(obj.start_time, obj.end_time)

    def get_gallery(self, obj: WorkshopEvent) -> list[str]:
        request = self.context.get('request')
        images = obj.gallery_images.order_by("sort_order", "id")
        urls = []
        for img in images:
            if img.image_url:
                url = request.build_absolute_uri(img.image_url.url) if request else img.image_url.url
                urls.append(url)
        return urls


class WorkshopEventAdminSerializer(serializers.ModelSerializer):
    gallery = EventGalleryImageSerializer(
        source="gallery_images", many=True, required=False
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    # ✅ Resolve to absolute asset string URLs
    image = serializers.SerializerMethodField()
    image_file = serializers.ImageField(source="image", write_only=True, required=False)

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
            "image_file",
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

    def get_image(self, obj) -> str | None:
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

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
    # ✅ Resolve to absolute asset string URLs
    src = serializers.SerializerMethodField()

    class Meta:
        model = SiteGalleryImage
        fields = ["src", "alt", "caption"]

    def get_src(self, obj) -> str | None:
        if obj.src:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.src.url) if request else obj.src.url
        return None


class SiteGalleryAdminSerializer(serializers.ModelSerializer):
    # ✅ Resolve to absolute asset string URLs
    src = serializers.SerializerMethodField()
    src_file = serializers.ImageField(source="src", write_only=True, required=False)

    class Meta:
        model = SiteGalleryImage
        fields = [
            "id",
            "src",
            "src_file",
            "alt",
            "caption",
            "sort_order",
            "is_published",
        ]

    def get_src(self, obj) -> str | None:
        if obj.src:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.src.url) if request else obj.src.url
        return None


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