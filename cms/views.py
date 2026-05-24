from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    ContactMessage,
    EventCategory,
    Host,
    SiteGalleryImage,
    SiteSettings,
    SocialLink,
    Testimonial,
    WorkshopEvent,
)
from .serializers import (
    ContactMessageCreateSerializer,
    ContactMessageSerializer,
    EventCategorySerializer,
    HostSerializer,
    SiteGalleryAdminSerializer,
    SiteGalleryPublicSerializer,
    SiteSettingsSerializer,
    SocialLinkSerializer,
    TestimonialAdminSerializer,
    TestimonialPublicSerializer,
    WorkshopEventAdminSerializer,
    WorkshopEventPublicSerializer,
)


class PublicEventViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = WorkshopEvent.objects.filter(is_published=True).select_related(
            "category", "host"
        ).prefetch_related("gallery_images")
        featured = self.request.query_params.get("featured")
        if featured and featured.lower() in ("1", "true", "yes"):
            qs = qs.filter(is_featured=True)
        return qs

    def get_serializer_class(self):
        return WorkshopEventPublicSerializer


class AdminEventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = WorkshopEvent.objects.select_related("category", "host").prefetch_related(
        "gallery_images"
    )
    serializer_class = WorkshopEventAdminSerializer
    lookup_field = "slug"


class PublicGalleryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = SiteGalleryPublicSerializer

    def get_queryset(self):
        return SiteGalleryImage.objects.filter(is_published=True)


class AdminGalleryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SiteGalleryImage.objects.all()
    serializer_class = SiteGalleryAdminSerializer


class PublicTestimonialViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = TestimonialPublicSerializer

    def get_queryset(self):
        return Testimonial.objects.filter(is_published=True)


class AdminTestimonialViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialAdminSerializer


class HostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Host.objects.all()
    serializer_class = HostSerializer


class EventCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer


class SocialLinkViewSet(viewsets.ModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(is_published=True)
        return qs


class SiteSettingsView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        settings = SiteSettings.load()
        return Response(SiteSettingsSerializer(settings).data)

    def patch(self, request):
        settings = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == "create":
            return ContactMessageCreateSerializer
        return ContactMessageSerializer

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save(update_fields=["is_read"])
        return Response(ContactMessageSerializer(message).data)


class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(
            {
                "events": WorkshopEvent.objects.count(),
                "published_events": WorkshopEvent.objects.filter(
                    is_published=True
                ).count(),
                "gallery_images": SiteGalleryImage.objects.count(),
                "testimonials": Testimonial.objects.count(),
                "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
                "hosts": Host.objects.count(),
            }
        )


class AdminMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        )
