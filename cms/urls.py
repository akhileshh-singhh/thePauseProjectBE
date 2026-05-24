from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r"events", views.PublicEventViewSet, basename="public-events")
router.register(r"gallery", views.PublicGalleryViewSet, basename="public-gallery")
router.register(
    r"testimonials", views.PublicTestimonialViewSet, basename="public-testimonials"
)
router.register(r"social", views.SocialLinkViewSet, basename="social-links")

admin_router = DefaultRouter()
admin_router.register(r"events", views.AdminEventViewSet, basename="admin-events")
admin_router.register(r"gallery", views.AdminGalleryViewSet, basename="admin-gallery")
admin_router.register(
    r"testimonials", views.AdminTestimonialViewSet, basename="admin-testimonials"
)
admin_router.register(r"hosts", views.HostViewSet, basename="admin-hosts")
admin_router.register(
    r"categories", views.EventCategoryViewSet, basename="admin-categories"
)
admin_router.register(
    r"messages", views.ContactMessageViewSet, basename="admin-messages"
)

urlpatterns = [
    path("", include(router.urls)),
    path("site/", views.SiteSettingsView.as_view(), name="site-settings"),
    path(
        "contact/",
        views.ContactMessageViewSet.as_view({"post": "create"}),
        name="contact-create",
    ),
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", views.AdminMeView.as_view(), name="auth-me"),
    path("admin/stats/", views.AdminStatsView.as_view(), name="admin-stats"),
    path("admin/", include(admin_router.urls)),
    path("admin/site/", views.SiteSettingsView.as_view(), name="admin-site-settings"),
]
