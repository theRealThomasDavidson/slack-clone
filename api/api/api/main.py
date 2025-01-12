from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from api.routes.auth import router as auth_router
from api.routes.users import router as users_router
from api.routes.channels import router as channels_router
from api.routes.chat import router as chat_router
from api.routes.files import router as files_router
from api.routes.reactions import router as reactions_router
from api.core.config import settings
from api.services.channel import ChannelService
from api.services.auth import AuthService

app = FastAPI(title=settings.APP_NAME)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on server startup"""
    # Services will initialize their own database sessions
    channel_service = ChannelService()
    auth_service = AuthService()

# Include routers with /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(channels_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(reactions_router, prefix="/api/v1")

# Add duplicate routes that include trailing slashes
for router in [auth_router, users_router, channels_router, chat_router, files_router, reactions_router]:
    for route in router.routes:
        path = route.path
        if not path.endswith('/'):
            # Create a new route with trailing slash that forwards to the original endpoint
            app.router.add_api_route(
                f"/api/v1{path}/",
                route.endpoint,
                methods=route.methods,
                response_model=route.response_model,
                status_code=route.status_code,
                tags=route.tags,
                dependencies=route.dependencies,
            )

@app.get("/")
async def root():
    return {"message": "Chat API V1"}
