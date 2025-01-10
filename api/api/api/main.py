from fastapi import FastAPI, WebSocket
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

# Include routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(channels_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(reactions_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Chat API V1"}
