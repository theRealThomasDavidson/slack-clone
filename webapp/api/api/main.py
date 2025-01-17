"""Main application module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.auth import router as auth_router
from api.routes.channel import router as channel_router
from api.routes.messages import router as messages_router
from api.routes.users import router as users_router
from api.routes.files import router as files_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(channel_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "API is running"} 