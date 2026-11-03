import time
from collections import defaultdict
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse
from app.core.config import settings

class RateLimitMiddleware:
    def __init__(self, app: ASGIApp, max_requests: int = settings.RATE_LIMIT_PER_MINUTE, window_seconds: int = 60):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts = defaultdict(list)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in ["/api/v1/health", "/api/v1/ready", "/docs", "/openapi.json"]:
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-content-type-options", b"nosniff"))
                    headers.append((b"x-frame-options", b"DENY"))
                    headers.append((b"x-xss-protection", b"1; mode=block"))
                    message["headers"] = headers
                await send(message)
            await self.app(scope, receive, send_wrapper)
            return

        client = scope.get("client")
        client_ip = client[0] if client else "unknown"
        now = time.time()

        timestamps = [ts for ts in self.request_counts[client_ip] if now - ts < self.window_seconds]
        if len(timestamps) >= self.max_requests:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please slow down your requests."}
            )
            await response(scope, receive, send)
            return

        timestamps.append(now)
        self.request_counts[client_ip] = timestamps

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-content-type-options", b"nosniff"))
                headers.append((b"x-frame-options", b"DENY"))
                headers.append((b"x-xss-protection", b"1; mode=block"))
                headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))
                headers.append((b"content-security-policy", b"default-src 'self'; frame-ancestors 'none';"))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
