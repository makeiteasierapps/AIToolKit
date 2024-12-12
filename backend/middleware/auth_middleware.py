from fastapi import status, HTTPException
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from backend.middleware.Oauth2 import refresh_access_token
from backend.config.logging_config import setup_logging

logger = setup_logging()

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = [
            '/auth/login', 
            '/auth/register', 
            '/auth/token', 
            '/static/', 
            '/favicon.ico', 
            '/auth/refresh'
        ]

    async def dispatch(self, request: Request, call_next):
        if self._is_public_path(request):
            return await call_next(request)

        access_token = request.cookies.get('access_token')
        refresh_token = request.cookies.get('refresh_token')

        if not self._is_valid_access_token(access_token):
            return await self._handle_invalid_access_token(request, refresh_token)

        return await self._process_request(request, call_next, refresh_token)

    def _is_public_path(self, request: Request) -> bool:
        return any(request.url.path.startswith(path) for path in self.public_paths)

    def _is_valid_access_token(self, access_token: str) -> bool:
        return access_token and access_token.startswith('Bearer ')

    def _is_html_request(self, request: Request) -> bool:
        return request.headers.get('accept', '').startswith('text/html')

    def _create_token_response(self, request: Request, new_token: str) -> RedirectResponse:
        response = RedirectResponse(
            url=request.url.path,
            status_code=status.HTTP_302_FOUND
        )
        response.set_cookie(
            key="access_token",
            value=f"Bearer {new_token}",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        return response

    async def _handle_invalid_access_token(self, request: Request, refresh_token: str):
        if refresh_token and self._is_html_request(request):
            try:
                new_token = refresh_access_token(refresh_token)
                return self._create_token_response(request, new_token)
            except Exception:
                return RedirectResponse(url='/auth/login')

        if self._is_html_request(request):
            return RedirectResponse(url='/auth/login')

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"}
        )

    async def _process_request(self, request: Request, call_next, refresh_token: str):
        try:
            # Add token to request headers
            request.headers.__dict__["_list"].append(
                (b'authorization', request.cookies['access_token'].encode())
            )
            
            response = await call_next(request)
            
            if response.status_code == status.HTTP_401_UNAUTHORIZED and refresh_token:
                return await self._handle_unauthorized_response(request, refresh_token)
            
            return response
            
        except HTTPException as e:
            raise e

    async def _handle_unauthorized_response(self, request: Request, refresh_token: str):
        try:
            new_token = refresh_access_token(refresh_token)
            return self._create_token_response(request, new_token)
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            if self._is_html_request(request):
                return RedirectResponse(url='/auth/login')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"}
            )