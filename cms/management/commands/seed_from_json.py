import json
from pathlib import Path

from django.core.management.base import BaseCommand

from cms.parse_schedule import parse_event_date, parse_event_times
from cms.models import (
    EventCategory,
    EventGalleryImage,
    Host,
    SiteGalleryImage,
    SiteSettings,
    SocialLink,
    Testimonial,
    WorkshopEvent,
)

DATA_DIR = Path(__file__).resolve().parents[4] / "data"


class Command(BaseCommand):
    help = "Import events, gallery, and testimonials from the Next.js JSON files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing CMS records before importing.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing CMS data…")
            EventGalleryImage.objects.all().delete()
            WorkshopEvent.objects.all().delete()
            Host.objects.all().delete()
            EventCategory.objects.all().delete()
            SiteGalleryImage.objects.all().delete()
            Testimonial.objects.all().delete()
            SocialLink.objects.all().delete()

        self._seed_events()
        self._seed_gallery()
        self._seed_testimonials()
        self._seed_social_defaults()
        self._seed_site_defaults()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def _seed_events(self) -> None:
        path = DATA_DIR / "events.json"
        if not path.exists():
            self.stderr.write(f"Missing {path}")
            return

        events = json.loads(path.read_text())
        for index, item in enumerate(events):
            category, _ = EventCategory.objects.get_or_create(
                name=item["category"],
                defaults={"sort_order": index},
            )
            host_data = item["host"]
            host, _ = Host.objects.get_or_create(
                name=host_data["name"],
                defaults={
                    "role": host_data["role"],
                    "bio": host_data["bio"],
                    "image": host_data["image"],
                },
            )
            start_time, end_time = parse_event_times(item["time"])
            event, created = WorkshopEvent.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "event_date": parse_event_date(item["date"]),
                    "start_time": start_time,
                    "end_time": end_time,
                    "venue": item["venue"],
                    "price_display": item["price"],
                    "image": item["image"],
                    "booking_link": item["bookingLink"],
                    "short_description": item["shortDescription"],
                    "description": item["description"],
                    "category": category,
                    "host": host,
                    "is_published": True,
                    "is_featured": True,
                    "sort_order": index,
                },
            )
            if created:
                self.stdout.write(f"  + event {event.slug}")
            event.gallery_images.all().delete()
            for g_index, url in enumerate(item.get("gallery", [])):
                EventGalleryImage.objects.create(
                    event=event, image_url=url, sort_order=g_index
                )

    def _seed_gallery(self) -> None:
        path = DATA_DIR / "gallery.json"
        if not path.exists():
            return
        images = json.loads(path.read_text())
        for index, item in enumerate(images):
            SiteGalleryImage.objects.update_or_create(
                src=item["src"],
                defaults={
                    "alt": item["alt"],
                    "caption": item.get("caption", ""),
                    "sort_order": index,
                    "is_published": True,
                },
            )

    def _seed_testimonials(self) -> None:
        path = DATA_DIR / "testimonials.json"
        if not path.exists():
            return
        rows = json.loads(path.read_text())
        for index, item in enumerate(rows):
            Testimonial.objects.update_or_create(
                name=item["name"],
                quote=item["quote"],
                defaults={
                    "context": item["context"],
                    "sort_order": index,
                    "is_published": True,
                },
            )

    def _seed_social_defaults(self) -> None:
        defaults = [
            {
                "platform": SocialLink.Platform.INSTAGRAM,
                "title": "Instagram",
                "description": "Daily pauses, studio glimpses, and ticket drops.",
                "href": "https://instagram.com/",
                "cta_label": "Follow",
                "sort_order": 0,
            },
            {
                "platform": SocialLink.Platform.LINKTREE,
                "title": "Linktree",
                "description": "All links in one calm place.",
                "href": "https://linktr.ee/",
                "cta_label": "Open",
                "sort_order": 1,
            },
            {
                "platform": SocialLink.Platform.WHATSAPP,
                "title": "WhatsApp",
                "description": "Quick questions and last-minute seats.",
                "href": "https://wa.me/919876543210",
                "cta_label": "Message",
                "sort_order": 2,
            },
        ]
        for item in defaults:
            SocialLink.objects.get_or_create(
                platform=item["platform"],
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "href": item["href"],
                    "cta_label": item["cta_label"],
                    "sort_order": item["sort_order"],
                    "is_published": True,
                },
            )

    def _seed_site_defaults(self) -> None:
        settings = SiteSettings.load()
        if not settings.hero_title:
            settings.hero_eyebrow = "Mumbai · Creative pauses"
            settings.hero_title = "Pause. Create. Feel."
            settings.hero_subtitle = (
                "Unhurried workshops for pottery, paint, journaling, and quiet connection."
            )
            settings.hero_cta_primary_label = "Upcoming events"
            settings.hero_cta_primary_href = "#events"
            settings.hero_cta_secondary_label = "Our story"
            settings.hero_cta_secondary_href = "#about"
            settings.contact_whatsapp_url = "https://wa.me/919876543210"
            settings.instagram_url = "https://instagram.com/"
            settings.footer_tagline = "Slow creative gatherings in Mumbai."
            settings.save()
