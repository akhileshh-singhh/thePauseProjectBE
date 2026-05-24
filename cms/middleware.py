"""
middleware.py — place this in your app directory (e.g. workshop/middleware.py)

Then register in settings.py MIDDLEWARE list:
    "workshop.middleware.RequestLoggingMiddleware",
    "workshop.middleware.AdminActionLoggingMiddleware",
"""

import json
import logging
import time

request_logger = logging.getLogger("workshop.requests")
auth_logger = logging.getLogger("workshop.auth")
admin_logger = logging.getLogger("workshop.admin")

# Paths that carry sensitive data — never log their bodies
SENSITIVE_PATHS = {
    "/api/auth/token/",
    "/api/auth/token/refresh/",
}

# Fields to scrub from any logged JSON body
SENSITIVE_FIELDS = {"password", "token", "access", "refresh", "secret", "authorization"}

# Admin paths that trigger CRUD action logging
ADMIN_PATHS_PREFIX = "/api/admin/"

# Map HTTP methods to action names
ACTION_MAP = {
    "POST": "CREATE",
    "PUT": "UPDATE",
    "PATCH": "PARTIAL_UPDATE",
    "DELETE": "DELETE",
    "GET": "READ",
}


def _scrub(data: dict) -> dict:
    """Recursively redact sensitive keys from a dict."""
    scrubbed = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_FIELDS:
            scrubbed[k] = "***REDACTED***"
        elif isinstance(v, dict):
            scrubbed[k] = _scrub(v)
        else:
            scrubbed[k] = v
    return scrubbed


def _safe_body(request) -> str:
    """Return a safe, scrubbed representation of the request body."""
    if request.path in SENSITIVE_PATHS:
        return "***SENSITIVE ENDPOINT — BODY HIDDEN***"
    try:
        body = request.body
        if not body:
            return ""
        data = json.loads(body)
        if isinstance(data, dict):
            return json.dumps(_scrub(data))
        return body.decode("utf-8", errors="replace")
    except (json.JSONDecodeError, Exception):
        return "<non-JSON body>"


def _get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


class RequestLoggingMiddleware:
    """
    Logs every request and response:
      - method, path, query string, client IP, user
      - response status and duration
      - request body (scrubbed) for mutating methods
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()

        user = (
            str(request.user)
            if hasattr(request, "user") and request.user.is_authenticated
            else "anonymous"
        )
        ip = _get_client_ip(request)
        qs = f"?{request.META['QUERY_STRING']}" if request.META.get("QUERY_STRING") else ""

        # Log incoming request
        if request.method in ("POST", "PUT", "PATCH"):
            body = _safe_body(request)
            request_logger.info(
                "REQUEST  %s %s%s | ip=%s user=%s | body=%s",
                request.method,
                request.path,
                qs,
                ip,
                user,
                body,
            )
        else:
            request_logger.info(
                "REQUEST  %s %s%s | ip=%s user=%s",
                request.method,
                request.path,
                qs,
                ip,
                user,
            )

        response = self.get_response(request)

        duration_ms = (time.monotonic() - start) * 1000
        level = logging.WARNING if response.status_code >= 400 else logging.INFO

        request_logger.log(
            level,
            "RESPONSE %s %s | status=%d duration=%.1fms user=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            user,
        )

        # Log 5xx as errors to errors.log as well
        if response.status_code >= 500:
            request_logger.error(
                "SERVER ERROR %s %s | status=%d ip=%s user=%s",
                request.method,
                request.path,
                response.status_code,
                ip,
                user,
            )

        return response


class AuthLoggingMiddleware:
    """
    Logs auth events:
      - token obtain attempts (success / failure)
      - token refresh attempts
      - access to /auth/me/
      - 401 / 403 responses on any endpoint
    """

    AUTH_PATHS = {
        "/api/auth/token/",
        "/api/auth/token/refresh/",
        "/api/auth/me/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = _get_client_ip(request)
        is_auth_path = request.path in self.AUTH_PATHS

        if is_auth_path:
            # Try to extract username for login attempts (never the password)
            username = "unknown"
            if request.path == "/api/auth/token/" and request.method == "POST":
                try:
                    data = json.loads(request.body)
                    username = data.get("username", "unknown")
                except Exception:
                    pass
            auth_logger.info(
                "AUTH ATTEMPT | path=%s method=%s ip=%s username=%s",
                request.path,
                request.method,
                ip,
                username,
            )

        response = self.get_response(request)

        if is_auth_path:
            if response.status_code == 200:
                auth_logger.info(
                    "AUTH SUCCESS | path=%s ip=%s username=%s",
                    request.path,
                    ip,
                    username if request.path == "/api/auth/token/" else "—",
                )
            elif response.status_code in (400, 401):
                auth_logger.warning(
                    "AUTH FAILURE | path=%s ip=%s username=%s status=%d",
                    request.path,
                    ip,
                    username if request.path == "/api/auth/token/" else "—",
                    response.status_code,
                )

        # Log 401/403 on any endpoint (unexpected auth failures)
        if response.status_code in (401, 403) and request.path not in self.AUTH_PATHS:
            auth_logger.warning(
                "ACCESS DENIED | %s %s | status=%d ip=%s user=%s",
                request.method,
                request.path,
                response.status_code,
                ip,
                getattr(request.user, "username", "anonymous"),
            )

        return response


class AdminActionLoggingMiddleware:
    """
    Logs all create/update/delete actions on admin endpoints.
    Attach the user and action so you have a full audit trail.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_admin = request.path.startswith(ADMIN_PATHS_PREFIX)
        is_mutating = request.method in ("POST", "PUT", "PATCH", "DELETE")

        response = self.get_response(request)

        if is_admin and is_mutating:
            action = ACTION_MAP.get(request.method, request.method)
            user = getattr(request.user, "username", "anonymous")
            ip = _get_client_ip(request)
            success = response.status_code < 400

            log_fn = admin_logger.info if success else admin_logger.warning
            log_fn(
                "ADMIN ACTION | action=%s path=%s | status=%d ip=%s user=%s | success=%s",
                action,
                request.path,
                response.status_code,
                ip,
                user,
                success,
            )

        return response
